from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime, timedelta
from app.fetch import fetch_rainfall_local, UnavailableData
from app.dependencies.config import Config

app = FastAPI()


@app.get("/")
async def root():
    return {
        "message": "Hello from weather-data service!",
        "config": config
    }


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
async def get_rainfall(
    time: datetime = datetime.now(),
    span: timedelta = timedelta(hours=1),
):
    """
    Get a TIFF format rainfall map. Unit: ??.

    Currently only accepts past dates if downloaded and a one hour span (using comephores).
    """
    try:
        path = fetch_rainfall_local(time, span)
        return FileResponse(path, media_type="image/tiff")

    except UnavailableData:
        return HTTPException(
            status_code=404, detail="Coméphores not downloaded for this period or span."
        )
