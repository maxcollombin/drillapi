import json
from typing import Annotated

from fastapi import FastAPI, Path, Request

from settings_values import cantons, globals
from src.services import get_canton_from_coordinates

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import httpx
from typing import Optional

import geopandas as gpd
from shapely.geometry import Point

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)


# start the app
app = FastAPI()

# Register exception handler for rate limit errors
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/v1/{coord_x}/{coord_y}")
@limiter.limit(globals.RATE_LIMIT)
async def get_drill_category(
    request: Request,
    coord_x: Annotated[
        float,
        Path(title="X coordinate of the location in EPSG:2056", gt=2400000, le=2900000),
    ],
    coord_y: Annotated[
        float,
        Path(title="Y coordinate of the location in EPSG:2056", gt=1070000, le=1300000),
    ],
):

    # Get canton corresponding to the coordinates using geoadmin api
    canton = get_canton_from_coordinates(coord_x, coord_y)
    code_canton = canton[0]["attributes"]["ak"]
    config = cantons.CANTONS.get(code_canton)

    # Calculate BBOX around the point (e.g. 20x20m square)
    delta = 10  # meters
    bbox = f"{coord_x - delta},{coord_y - delta},{coord_x + delta},{coord_y + delta}"

    # WMS request parameters for ground category
    wms_url = config["wmsUrl"]
    params_wms = {
        "SERVICE": "WMS",
        "VERSION": "1.3.0",
        "REQUEST": "GetFeatureInfo",
        "QUERY_LAYERS": config["layers"][0]["name"],
        "LAYERS": config["layers"][0]["name"],
        "INFO_FORMAT": "application/geo+json",
        "I": "50",
        "J": "50",
        "CRS": "EPSG:2056",
        "WIDTH": "101",
        "HEIGHT": "101",
        "BBOX": bbox,
    }

    # results initialisation
    ground_type = None
    in_consultation = False

    # Request for ground type
    try:
        with httpx.Client(timeout=20.0) as client:
            response_ground = client.get(wms_url, params=params_wms)
            response_ground.raise_for_status()
            geojson_data = response_ground.json()
            features = geojson_data.get("features", [])
            if features:
                properties = features[0].get("properties", {})
                ground_type = properties.get("Type", "Type inconnu")
            else:
                ground_type = "Information not available."
    except Exception as e:
        ground_type = "Error"

        # Verify intersection with consultation area if applicable
        try:
            gdf = gpd.read_file("data/rohrleitungen_konsultationsbereich.gpkg")
            gdf = gdf.to_crs(epsg=2056)
            point = Point(coord_x, coord_y)
            in_consultation = gdf.intersects(point).any()
        except Exception as e:
            in_consultation = "Error"

    return {
        "coord_x": coord_x,
        "coord_y": coord_y,
        "canton": code_canton,
        "ground_category": ground_type,
        "in_consultation_area": in_consultation,
    }


"""Display list of cantons available in the API."""


@app.get("/v1/cantons")
@limiter.limit(globals.RATE_LIMIT)
async def get_canton(
    request: Request,
):
    return cantons.CANTONS
