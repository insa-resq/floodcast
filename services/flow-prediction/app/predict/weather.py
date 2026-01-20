from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

import httpx
from pydantic import BaseModel
from rasterio.io import (  # pyright: ignore[reportMissingTypeStubs]
    DatasetReader,
    MemoryFile,
)

BASE_URL = "http://weather-data-service:8000"
# BASE_URL = "http://localhost:8001"


# Times and spans must be on the hour
class AvailabilityPeriod(BaseModel):
    start: datetime
    span: timedelta


# Rainfall data unit:
# kg.m-2
@asynccontextmanager
async def rainfall_data(
    params: AvailabilityPeriod,
    client: httpx.AsyncClient | None = None,
) -> AsyncIterator[DatasetReader]:
    """
    Fetch the /rainfall endpoint and open the returned TIFF with rasterio.

    Yields
    ------
    rasterio.io.DatasetReader
        An open rasterio dataset.
    """

    close_client = client is None
    if close_client:
        client = httpx.AsyncClient(timeout=None)

    try:
        response = await client.get(f"{BASE_URL}/rainfall", params=params.model_dump())

        if response.status_code == 404:
            raise FileNotFoundError(
                "Rainfall data not available for this period or span."
            )

        _ = response.raise_for_status()

        tiff_bytes = response.content

        with MemoryFile(tiff_bytes) as memfile:
            with memfile.open() as dataset:
                yield dataset

    finally:
        if close_client:
            await client.aclose()
