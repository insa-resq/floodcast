from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse

from app.cache import fetch_rainfall_cached
from app.dependencies.config import Config
from app.fetch import (
    UnavailableData,
    fetch_rainfall_availability_local,
    fetch_rainfall_local,
)
from app.models import AvailabilityPeriod

app = FastAPI()


@app.get("/")
async def root(config: Config):
    return {"message": "Hello from weather-data service!", "config": config}


@app.get("/availability/local", response_model=list[AvailabilityPeriod])
async def get_availability_local():
    """
    Get the list of available rainfall periods.
    """
    return list(fetch_rainfall_availability_local())


@app.get(
    "/rainfall",
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
    bytes = await fetch_rainfall_cached(availability)
    return Response(bytes, media_type="image/tiff")

    # except:  # noqa: E722
    #     return HTTPException(status_code=404, detail="No data for this period or span.")


@app.get(
    "/rainfall/local",
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
async def get_rainfall_local(availability: Annotated[AvailabilityPeriod, Query()]):
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
