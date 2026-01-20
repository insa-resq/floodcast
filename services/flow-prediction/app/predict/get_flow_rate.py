from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta
from typing import Literal

import httpx
from pydantic import BaseModel
from rasterio.io import (  # pyright: ignore[reportMissingTypeStubs]
    DatasetReader,
    MemoryFile,
)

BASE_URL = "http://flow-data-service:8000"
# BASE_URL = "http://localhost:8002"


class SiteInfo(BaseModel):
    code: str
    longitude: float
    latitude: float
    river: str


class FlowInfo(BaseModel):
    site_info: SiteInfo
    obs_date: datetime
    measure: Literal["Q", "H"]
    value: float


class LatestFlowQueryParams(BaseModel):
    latitude: float
    longitude: float
    max_distance: int


async def get_flow_rate_data(
    params: LatestFlowQueryParams,
) -> FlowInfo:
    """
    Fetch the /rainfall endpoint and open the returned TIFF with rasterio.

    Yields
    ------
    rasterio.io.DatasetReader
        An open rasterio dataset.
    """

    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.get(
            f"{BASE_URL}/measurements/flow/latest", params=params.model_dump()
        )

        _ = response.raise_for_status()

        return FlowInfo.model_validate_json(response.text)
