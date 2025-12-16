from datetime import datetime
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
<<<<<<< HEAD
from datetime import datetime, timedelta
from app.fetch import fetch_rainfall_local, UnavailableData
from app.dependencies.config import Config
||||||| parent of 433c495 (Add availability endpoint and pydantic data model)
from datetime import datetime, timedelta
from app.fetch import fetch_rainfall_local, UnavailableData
=======

from app.fetch import UnavailableData, fetch_rainfall_local, fetch_rainfall_availability_local
from app.models import AvailabilityPeriod
>>>>>>> 433c495 (Add availability endpoint and pydantic data model)

app = FastAPI()


@app.get("/")
async def root():
    return {
        "message": "Hello from weather-data service!",
        "config": config
    }


@app.get("/availability", response_model=list[AvailabilityPeriod])
async def get_availability():
    """
    Get the list of available rainfall periods.
    """
    return list(fetch_rainfall_availability_local())


@app.get(
    "/rainfall",
    response_class=FileResponse,
    responses={
        200: {
            "content": {"image/tiff": {}},
            "description": "TIFF file returned successfully",
        },
        404: {
            "description": "File not found",
        },
        500: {
            "description": "Server error while generating file",
        },
    },
)
async def get_rainfall(availability: Annotated[AvailabilityPeriod, Query()]):
    """
    Get a TIFF format rainfall map. Unit: ??.

    Currently only accepts past dates if downloaded and a one hour span (using comephores).
    """
    try:
        path = fetch_rainfall_local(availability)
        return FileResponse(path, media_type="image/tiff")

    except UnavailableData:
        return HTTPException(
            status_code=404, detail="Coméphores not downloaded for this period or span."
        )
