from typing import Annotated, Literal
from fastapi import Depends
from pydantic import BaseModel
from httpx import AsyncClient
from async_lru import alru_cache


class ConfigModel(BaseModel):
    log_level: Literal["debug"]


@alru_cache(maxsize=32)
async def fetch_config() -> ConfigModel:
    url = "http://config-service:8000/config/weather-data"
    async with AsyncClient() as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()
        return ConfigModel(**data["config"])

async def get_config() -> ConfigModel:
    return await fetch_config()

Config = Annotated[ConfigModel, Depends(get_config)]
