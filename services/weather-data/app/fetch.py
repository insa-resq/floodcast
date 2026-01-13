import os
import re
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import AsyncIterator, Generator, Literal, Optional

import httpx
import isodate
from lxml import etree
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
    # Forecast time
    # TODO: Serialize as subset: str = f"time({time})"
    time: datetime
    coverage_id: str = Field(serialization_alias="coverageid")
    service: Literal["WCS"] = "WCS"
    version: Literal["2.0.1"] = "2.0.1"
    format: Literal["image/tiff"] = "image/tiff"

    @field_serializer("time")
    def serialize_time_as_subset(self, time: datetime, _info):
        """
        Serialize `time` as a WCS subset parameter.
        """

        return f"time({time.isoformat()}Z)"

    def model_dump(self, *args, **kwargs):
        """
        Override dump to rename `time` → `subset`
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
    r"(?P<datetime>\d{4}-\d{2}-\d{2}T\d{2}\.\d{2}\.\d{2}Z)"
    r"_(?P<period>.+)$"
)


async def fetch_availability() -> AsyncIterator[tuple[str, datetime, timedelta]]:
    """
    Iterates over CoverageIds matching TOTAL_WATER_PRECIPITATION pattern.

    Yields:
        (coverage_id, datetime, period)
    """
    async with httpx.AsyncClient(timeout=None) as client:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(
                BASE_URL + "/GetCapabilities",
                params=CapabilitiesQueryParams().model_dump(),
                headers={"apikey": METEO_FRANCE_AROME_API_KEY},
            )
            response.raise_for_status()

            # Load the entire XML into memory
            xml_root = etree.fromstring(response.content)

            # Iterate over all CoverageId elements
            for coverage_elem in xml_root.xpath(
                ".//wcs:CoverageId",
                namespaces={"wcs": "http://www.opengis.net/wcs/2.0"},
            ):
                coverage_id = coverage_elem.text.strip()

                match = COVERAGE_ID_PATTERN.match(coverage_id)
                if match:
                    dt_raw = match.group("datetime")
                    period_str = match.group("period")

                    # Convert datetime
                    dt = datetime.strptime(dt_raw, "%Y-%m-%dT%H.%M.%SZ")

                    # Parse ISO-8601 duration
                    duration = isodate.parse_duration(period_str)

                    yield coverage_id, dt, duration


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
) -> Optional[str]:
    """
    Given a target period, select the best coverageId.
    coverage_list: list of tuples (coverage_id, dt, period)
    """
    valid_coverages = [
        c
        for c in coverage_list
        if c[1] <= period.start - timedelta(hours=1) and c[2] == period.span
    ]

    if valid_coverages:
        # pick the coverageId of the latest past time
        best = max(valid_coverages, key=lambda c: c[1])
    else:
        return None

    return best[0]


async def fetch_rainfall(period: AvailabilityPeriod) -> BytesIO:
    # Determine the best coverageId for the period
    # If period is in the past, use the coverageId of that hour
    # Otherwise, use the latest coverageID

    #  Build list of all available TOTAL_WATER_PRECIPITATION coverageIds
    coverage_list = [(cid, dt, span) async for cid, dt, span in fetch_availability()]

    if not coverage_list:
        raise ValueError("No matching coverageIds found in the capabilities XML.")

    # Determine best coverageId for the period
    best_coverage_id = select_best_coverage_id(period, coverage_list)
    if best_coverage_id is None:
        raise ValueError("Could not find a coverageId for the requested period.")

    # Create CoverageQueryParams
    params = CoverageQueryParams(
        coverage_id=best_coverage_id,
        time=period.start,
    )
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.get(
            f"{BASE_URL}/GetCoverage",
            params=params.model_dump(by_alias=True),
            headers={"apikey": METEO_FRANCE_AROME_API_KEY},
        )
        response.raise_for_status()

        return BytesIO(response.content)


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
        bytes = await fetch_rainfall(
            AvailabilityPeriod(
                start=datetime(year=2026, month=1, day=13, hour=12),
                span=timedelta(hours=1),
            )
        )
        # Write the stuff
        with open("output.tiff", "wb") as f:
            f.write(bytes.getbuffer())

    asyncio.run(test())
