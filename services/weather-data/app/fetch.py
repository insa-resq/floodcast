from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import Generator

import httpx

from app.models import AvailabilityPeriod

# TODO
BASE_URL = "https://..."
BASE_PATH = Path(__file__).parent.parent / "comephores"
FILE_PATTERN = "%Y%m%d%H_ERR.gtif"


class UnavailableData(Exception):
    pass


async def fetch_rainfall_availability() -> Generator[AvailabilityPeriod]:
    # TODO
    pass


def fetch_rainfall_availability_local() -> Generator[AvailabilityPeriod]:
    for file in BASE_PATH.glob("*.gtif"):
        try:
            yield AvailabilityPeriod(
                start=datetime.strptime(file.name, FILE_PATTERN), span=timedelta(hours=1)
            )
        except ValueError:
            print(f"Warning: comephore file did not match pattern: {file.name}")


async def fetch_rainfall(period: AvailabilityPeriod) -> BytesIO:
    async with httpx.AsyncClient() as client:
        r = await client.get(BASE_URL)
        return BytesIO(r.content)


def fetch_rainfall_local(period: AvailabilityPeriod) -> Path:
    if period.span != timedelta(hours=1):
        raise UnavailableData()
    path = BASE_PATH / period.start.strftime(FILE_PATTERN)
    if not path.is_file():
        raise UnavailableData()
    return path
