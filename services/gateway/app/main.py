from fastapi import FastAPI
import httpx
import logging

# from app.dependencies.config import Config
from app.dependencies.config import Config
from app.models import Segment, Flood, User, AvailabilityPeriod
from datetime import datetime, timedelta

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
async def subscribe(user: User) -> User:
    return user

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
async def get_floods() -> list[Flood]:
    return [Flood(
        id=1,
        segments_ids=[1, 2],
        severity=3,
        probability=0.75,
        period=AvailabilityPeriod(
            start=datetime(2025, 9, 9, 12),
            span=timedelta(hours=1)
        )
    )]

@app.get("/floods/{departement}")
async def get_floods_departement(departement: int) -> list[Flood]:
    return [Flood(
        id=1,
        segments_ids=[1, 2],
        severity=3,
        probability=0.75,
        period=AvailabilityPeriod(
            start=datetime(2025, 9, 9, 12),
            span=timedelta(hours=1)
        )
    )]

@app.get("/floods/{id}")
async def get_flood(id: int) -> Flood:
    return Flood(
        id=id,
        segments_ids=[1, 2],
        severity=3,
        probability=0.75,
        period=AvailabilityPeriod(
            start=datetime(2025, 9, 9, 12),
            span=timedelta(hours=1)
        )
    )

@app.get("/floods/{id}/map")
async def get_flood_map(id: int):
    return