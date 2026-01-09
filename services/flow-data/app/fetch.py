from datetime import date
from typing import Literal

from httpx import AsyncClient
from pydantic import BaseModel, Field, OnErrorOmit, model_serializer, model_validator

BASE_URL = "https://hubeau.eaufrance.fr/api/v2/hydrometrie"


class SiteInfo(BaseModel):
    code: str = Field(validation_alias="code_site")
    longitude: float = Field(validation_alias="longitude_site")
    latitude: float = Field(validation_alias="latitude_site")
    river: str = Field(validation_alias="libelle_cours_eau")


class SiteQueryResponse(BaseModel):
    data: list[SiteInfo]


class SiteQueryParams(BaseModel):
    latitude: float
    longitude: float
    max_distance: int = Field(serialization_alias="distance")
    river: str = Field(default="La Garonne", serialization_alias="libelle_cours_eau")
    active: Literal[True] = Field(default=True, serialization_alias="en_service")


async def locate_nearest_station(query: SiteQueryParams) -> SiteInfo | None:
    async with AsyncClient() as client:
        r = await client.get(
            BASE_URL + "/referentiel/sites",
            params=query.model_dump(by_alias=True, exclude_none=True),
        )
    stations = SiteQueryResponse.model_validate_json(r.text)
    if len(stations.data) == 0:
        return None
    return min(
        stations.data,
        key=lambda s: (s.latitude - query.latitude) ** 2
        + (s.longitude - query.longitude) ** 2,
    )


class FlowQueryParams(BaseModel):
    latitude: float
    longitude: float
    max_distance: int = Field(serialization_alias="distance")
    # site_code: str = Field(serialization_alias="code_entite")
    start_date: date | None = Field(
        default=None, serialization_alias="date_debut_obs_elab"
    )
    end_date: date | None = Field(default=None, serialization_alias="date_fin_obs_elab")


class FlowInfo(BaseModel):
    site_info: SiteInfo
    obs_date: date = Field(validation_alias="date_obs_elab")
    measure: Literal["Q", "H"]
    measure_type: Literal["average", "min", "max"]
    span: Literal["daily", "monthly"]
    value: float = Field(validation_alias="resultat_obs_elab")

    @model_validator(mode="before")
    @classmethod
    def decompose_measure(cls, data: dict):
        measure_raw = data.get("grandeur_hydro_elab")
        if measure_raw:
            data["measure"] = measure_raw[0]
            if data["measure"] == "Q":
                data["resultat_obs_elab"] /= 60
            else:
                data["resultat_obs_elab"] /= 100
            if "ix" in measure_raw.lower():
                data["measure_type"] = "max"
            elif "in" in measure_raw.lower():
                data["measure_type"] = "min"
            else:
                data["measure_type"] = "average"
            data["span"] = "daily" if "nj" in measure_raw.lower() else "monthly"

        if any(x in data for x in ["code_site", "longitude", "latitude"]):
            data = data.copy()
            data["site_info"] = {
                "code_site": data.pop("code_site", None),
                "longitude_site": data.pop("longitude", None),
                "latitude_site": data.pop("latitude", None),
                "libelle_cours_eau": "La Garonne",
            }
        return data


class FlowResponse(BaseModel):
    data: list[OnErrorOmit[FlowInfo]]
    # data: list[FlowInfo]


async def fetch_flows(query: FlowQueryParams) -> FlowResponse:
    async with AsyncClient() as client:
        r = await client.get(
            BASE_URL + "/obs_elab",
            params=query.model_dump(by_alias=True, exclude_none=True),
        )
    stations = FlowResponse.model_validate_json(r.text)
    return stations


def latest_measure(
    flows: FlowResponse,
    measure: Literal["Q", "H"],
    measure_type: Literal["average", "min", "max"],
    span: Literal["daily", "monthly"],
) -> FlowInfo | None:
    filtered = filter(
        lambda f: f.measure == measure
        and f.measure_type == measure_type
        and f.span == span,
        flows.data,
    )
    try:
        return max(filtered, key=lambda x: x.obs_date)
    except:
        return None


if __name__ == "__main__":
    import asyncio

    async def test():
        flows = await fetch_flows(
            FlowQueryParams(
                latitude=43.604652,
                longitude=1.444209,
                max_distance=10,
                start_date=date(year=2026, month=1, day=1),
            )
        )
        print(latest_measure(flows, measure="H", measure_type="max", span="daily"))

    asyncio.run(test())
