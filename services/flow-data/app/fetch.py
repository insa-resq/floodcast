from datetime import date, datetime
from typing import Literal

from httpx import AsyncClient
from pydantic import BaseModel, Field, OnErrorOmit, model_validator

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
    start_date: datetime | None = Field(
        default=None, serialization_alias="date_debut_obs"
    )
    end_date: datetime | None = Field(default=None, serialization_alias="date_fin_obs")
    measure: Literal["Q", "H"] = Field(
        default="Q", serialization_alias="grandeur_hydro"
    )


class FlowInfo(BaseModel):
    site_info: SiteInfo
    obs_date: datetime = Field(validation_alias="date_obs")
    measure: Literal["Q", "H"] = Field(validation_alias="grandeur_hydro")
    value: float = Field(validation_alias="resultat_obs")

    @model_validator(mode="before")
    @classmethod
    def decompose_measure(cls, data: dict):
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
    # data: list[OnErrorOmit[FlowInfo]]
    data: list[FlowInfo]


async def fetch_flows(query: FlowQueryParams) -> FlowResponse:
    async with AsyncClient() as client:
        r = await client.get(
            BASE_URL + "/observations_tr",
            params=query.model_dump(by_alias=True, exclude_none=True),
        )
    stations = FlowResponse.model_validate_json(r.text, by_alias=True)
    return stations


def latest_measure(
    flows: FlowResponse,
    measure: Literal["Q", "H"],
) -> FlowInfo | None:
    filtered = filter(
        lambda f: f.measure == measure,
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
                start_date=datetime(year=2026, month=1, day=1),
            )
        )
        print(
            latest_measure(
                flows,
                measure="Q",
            )
        )

    asyncio.run(test())
