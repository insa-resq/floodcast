from typing import Annotated, Literal
from fastapi import Depends
from httpx import AsyncClient
from async_lru import alru_cache
from pydantic import BaseModel


class Routes(BaseModel):
    weather_data: str

class ConfigModel(BaseModel):
    log_level: Literal["info", "debug"]
    routes: Routes

@alru_cache(maxsize=32)
async def fetch_config() -> ConfigModel:
    url = "http://config-service:8000/config/gateway"
    async with AsyncClient() as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()
        return ConfigModel(**data["config"])

async def get_config() -> ConfigModel:
    return await fetch_config()


Config = Annotated[ConfigModel, Depends(get_config)]
