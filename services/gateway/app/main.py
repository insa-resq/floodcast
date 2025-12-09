from fastapi import FastAPI
import httpx
from app.models import Segment, Flood, User, AvailabilityPeriod
from datetime import datetime, timedelta

app = FastAPI()

@app.get("/")
async def root():
    async with httpx.AsyncClient() as client:
        r = await client.get("http://weather-data-service:8000")
        return {"message": "Hello from gateway service!", "weather": r.json()}

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