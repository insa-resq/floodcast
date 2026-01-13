from fastapi import FastAPI, HTTPException
import httpx
import logging

# from app.dependencies.config import Config
from app.dependencies.config import Config
from app.models import Segment, PredictionModel, UserModel
from datetime import datetime

app = FastAPI()
logger = logging.getLogger("gateway")

@app.get("/")
async def root(config: Config):
    # appel du microservice météo pour vérifier que tout marche
    weather_url = config.routes.weather_data
    async with httpx.AsyncClient() as client:
        r = await client.get(weather_url)
        weather = r.json()

    return {
        "message": "Hello from gateway service!",
        "config": config.model_dump,
        "weather": weather,
    }
@app.post("/subscribe")
async def subscribe(user: UserModel):
    url = "http://alert-service:8000/subscribe"
    async with httpx.AsyncClient() as client:
        r = await client.post(url, data={"data": user})
        r.raise_for_status()

@app.get("/segments")
async def get_segments() -> list[Segment]:
    segment = Segment(
        id=1,
        lat_1=48,
        long_1=2,
        lat_2=51,
        long_2=4,
    )
    return [segment]

@app.get("/segments/{id}")
async def get_segment(id: int) -> Segment:
    segment = Segment(
        id=id,
        lat_1=48,
        long_1=2,
        lat_2=51,
        long_2=4,
    )
    return segment

@app.get("/floods")
async def get_floods() -> list[PredictionModel]:
    url = "http://inference-service:8000/predictions"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()
        floods = [PredictionModel(**item) for item in data]
        return floods

@app.get("/floods/{id}")
async def get_flood_by_id(id: int) -> PredictionModel:
    url = f"http://inference-service:8000/predictions/{id}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()
        return PredictionModel(**data)

@app.get("/floods/{id}/map")
async def get_flood_map(id: int):
    return