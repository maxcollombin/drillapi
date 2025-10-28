from typing import Union
from typing import Annotated

from fastapi import FastAPI, Path, Query

from settings_cantons import cantons
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

# Initialize the Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    lambda request, exc: JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
    ),
)

app = FastAPI()


@app.get("/v1/{coord_x}/{coord_y}", dependencies=[limiter.limit("10/minute")])
async def get_drill_category(
    coord_x: Annotated[
        float,
        Path(title="X coordinate of the location in EPSG:2056", gt=2400000, le=2900000),
    ],
    coord_y: Annotated[
        float,
        Path(title="Y coordinate of the location in EPSG:2056", gt=1070000, le=1300000),
    ],
):

    for item in cantons.CANTONS_LIST:
        print(item)

    # TODO: Implement logic to determine drill category based on coordinates

    return {"coord_x": coord_x, "coord_y": coord_y, "drill_category": "Not Implemented"}


"""Display list of cantons available in the API."""


@app.get("/v1/cantons", dependencies=[limiter.limit("10/minute")])
async def get_drill_category():
    return cantons.CANTONS_LIST
