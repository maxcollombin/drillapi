from typing import Annotated

from fastapi import FastAPI, Path, Request

from settings_values import cantons, globals
from src.services import get_canton_from_coordinates

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import httpx
from typing import Optional

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

    return {"coord_x": coord_x, "coord_y": coord_y, "canton": canton}


"""Display list of cantons available in the API."""


@app.get("/v1/cantons")
@limiter.limit(globals.RATE_LIMIT)
async def get_canton(
    request: Request,
):
    return cantons.CANTONS_LIST
