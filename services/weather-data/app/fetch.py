import os
import re
from collections.abc import AsyncIterator, Generator
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import Literal, override

import httpx
import isodate  # pyright: ignore[reportMissingTypeStubs]
from async_lru import alru_cache
from lxml import (  # pyright: ignore[reportMissingTypeStubs]
    etree,  # pyright: ignore[reportAttributeAccessIssue ]
)
from pydantic import BaseModel, Field, field_serializer

from app.models import AvailabilityPeriod

# TODO
METEO_FRANCE_AROME_API_KEY = os.environ["METEO_FRANCE_AROME_API_KEY"]
# Datetime here is the date at which the forecast was published. Period is the time over which it is accumulated.
COVERAGE_ID = "TOTAL_WATER_PRECIPITATION__GROUND_OR_WATER_SURFACE___{datetime}_{period}"
BASE_URL = "https://public-api.meteofrance.fr/public/arome/1.0/wcs/MF-NWP-HIGHRES-AROME-0025-FRANCE-WCS"
BASE_PATH = Path(__file__).parent.parent / "comephores"
FILE_PATTERN = "%Y%m%d%H_ERR.gtif"


class CoverageQueryParams(BaseModel):
    time: datetime
    coverage_id: str = Field(serialization_alias="coverageid")
    service: Literal["WCS"] = "WCS"
    version: Literal["2.0.1"] = "2.0.1"
    format: Literal["image/tiff"] = "image/tiff"

    @field_serializer("time")
    def serialize_time_as_subset(self, time: datetime):
        """
        Serialize time as a WCS subset parameter.
        """

        return f"time({time.isoformat()}Z)"

    @override
    def model_dump(self, *args, **kwargs):  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
        """
        Override dump to rename time → subset
        """
        data = super().model_dump(*args, **kwargs)
        data["subset"] = data.pop("time")
        return data


class UnavailableData(Exception):
    pass


class CapabilitiesQueryParams(BaseModel):
    service: Literal["WCS"] = "WCS"
    version: Literal["2.0.1"] = "2.0.1"
    language: Literal["eng"] = "eng"


COVERAGE_ID_PATTERN = re.compile(
    r"^TOTAL_WATER_PRECIPITATION__GROUND_OR_WATER_SURFACE___"
    + r"(?P<datetime>\d{4}-\d{2}-\d{2}T\d{2}\.\d{2}\.\d{2}Z)"
    + r"_(?P<period>.+)$"
)


# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false
async def fetch_coverage_ids() -> AsyncIterator[tuple[str, datetime, timedelta]]:
    """
    Calls GET /GetCapabilities, fetches all coverage_ids matching TOTAL_WATER_PRECIPITATION pattern.
    Extracts the time at which the forecast was made and the accumulation period.

    Yields:
        (coverage_id, datetime, period)
    """
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(
            BASE_URL + "/GetCapabilities",
            params=CapabilitiesQueryParams().model_dump(),
            headers={"apikey": METEO_FRANCE_AROME_API_KEY},
        )
        _ = response.raise_for_status()

        # Load the entire XML into memory
        xml_root = etree.fromstring(response.content)
        # Iterate over all CoverageId elements
        for coverage_elem in xml_root.xpath(
            ".//wcs:CoverageId",
            namespaces={"wcs": "http://www.opengis.net/wcs/2.0"},
        ):
            coverage_id = coverage_elem.text.strip()

            match = COVERAGE_ID_PATTERN.match(coverage_id)  # pyright: ignore[reportUnknownArgumentType]
            if match:
                dt_raw = match.group("datetime")
                period_str = match.group("period")

                # Convert datetime
                dt = datetime.strptime(dt_raw, "%Y-%m-%dT%H.%M.%SZ")

                # Parse ISO-8601 duration
                duration = isodate.parse_duration(period_str)

                yield coverage_id, dt, duration


@alru_cache(ttl=3600)
async def fetch_coverage_ids_cached() -> list[tuple[str, datetime, timedelta]]:
    res = [c async for c in fetch_coverage_ids()]
    if not res:
        raise ValueError("No coverage ids found")
    return res


def fetch_rainfall_availability_local() -> Generator[AvailabilityPeriod]:
    for file in BASE_PATH.glob("*.gtif"):
        try:
            yield AvailabilityPeriod(
                start=datetime.strptime(file.name, FILE_PATTERN),
                span=timedelta(hours=1),
            )
        except ValueError:
            print(f"Warning: comephore file did not match pattern: {file.name}")


def select_best_coverage_id(
    period: AvailabilityPeriod,
    coverage_list: list[tuple[str, datetime, timedelta]],
) -> str | None:
    """
    Given a target period, select the best coverageId.
    coverage_list: list of tuples (coverage_id, dt, period)
    """
    valid_coverages = [
        c for c in coverage_list if c[1] <= period.start and c[2] == period.span
    ]

    if valid_coverages:
        # pick the coverageId of the latest past time
        return max(valid_coverages, key=lambda c: c[1])[0]
    else:
        return None


async def fetch_rainfall(period: AvailabilityPeriod) -> bytes:
    # Determine the best coverageId for the period
    # If period is in the past, use the coverageId of that hour
    # Otherwise, use the latest coverageID

    #  Build list of all available TOTAL_WATER_PRECIPITATION coverageIds
    coverage_list = await fetch_coverage_ids_cached()

    if not coverage_list:
        raise ValueError("No matching coverageIds found in the capabilities XML.")

    # Determine best coverageId for the period
    best_coverage_id = select_best_coverage_id(period, coverage_list)
    if best_coverage_id is None:
        raise ValueError("Could not find a coverageId for the requested period.")
    print(best_coverage_id)

    # Create CoverageQueryParams
    params = CoverageQueryParams(
        coverage_id=best_coverage_id,
        time=period.start + period.span,
    )
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(
            f"{BASE_URL}/GetCoverage",
            params=params.model_dump(by_alias=True),
            headers={"apikey": METEO_FRANCE_AROME_API_KEY},
        )
        _ = response.raise_for_status()

        return response.content


def fetch_rainfall_local(period: AvailabilityPeriod) -> Path:
    if period.span != timedelta(hours=1):
        raise UnavailableData()
    path = BASE_PATH / period.start.strftime(FILE_PATTERN)
    if not path.is_file():
        raise UnavailableData()
    return path


if __name__ == "__main__":
    import asyncio

    async def test():
        # bytes = await fetch_rainfall(
        #     AvailabilityPeriod(
        #         start=datetime(year=2026, month=1, day=13, hour=12),
        #         span=timedelta(hours=1),
        #     )
        # )
        # with open("output.tiff", "wb") as f:
        #     _ = f.write(bytes.getbuffer())
        async for id in fetch_coverage_ids():
            print(id)

    asyncio.run(test())
