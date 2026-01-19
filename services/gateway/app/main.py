from typing import List
from fastapi import FastAPI, HTTPException
import httpx
import logging

# from app.dependencies.config import Config
from app.dependencies.config import Config
from app.models import Segment, PredictionModel, UserModel

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


@app.post("/subscribe", status_code=201)
async def subscribe(user: UserModel):
    url = "http://alert-service:8000/subscribe"
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=user.model_dump())
            r.raise_for_status()
    except httpx.HTTPError as e:
        logger.error(f"Alert service error: {e}")
        raise HTTPException(status_code=502, detail="Alert service unavailable")

    return {"status": "subscribed"}


@app.get("/segments", response_model=List[Segment])
async def get_segments():
    segment = Segment(
        id=1,
        lat_1=48,
        long_1=2,
        lat_2=51,
        long_2=4,
    )
    return [segment]


@app.get("/segments/{id}", response_model=Segment)
async def get_segment(id: int):
    segment = Segment(
        id=id,
        lat_1=48,
        long_1=2,
        lat_2=51,
        long_2=4,
    )
    return segment


@app.get("/floods", response_model=List[PredictionModel])
async def get_floods():
    url = "http://inference-service:8000/predictions"
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            r.raise_for_status()
            data = r.json()
    except httpx.HTTPStatusError as e:
        status = e.response.status_code
        text = e.response.text
        logger.error(f"Inference service returned {status}: {text}")

        if status == 404:
            raise HTTPException(status_code=404, detail="Predictions not found")
        else:
            raise HTTPException(status_code=502, detail="Inference service error")

    except httpx.RequestError as e:
        logger.error(f"Inference service unavailable: {e}")
        raise HTTPException(status_code=502, detail="Inference service unavailable")

    return [PredictionModel(**item) for item in data]


@app.get("/floods/{id}", response_model=PredictionModel)
async def get_flood_by_id(id: int):
    url = f"http://inference-service:8000/predictions/{id}"
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            r.raise_for_status()
            data = r.json()
    except httpx.HTTPStatusError as e:
        status = e.response.status_code
        text = e.response.text
        logger.error(f"Inference service returned {status}: {text}")

        if status == 404:
            raise HTTPException(status_code=404, detail="Prediction not found")
        else:
            raise HTTPException(status_code=502, detail="Inference service error")

    except httpx.RequestError as e:
        logger.error(f"Inference service unavailable: {e}")
        raise HTTPException(status_code=502, detail="Inference service unavailable")

    return PredictionModel(**data)


@app.get("/floods/{id}/map")
async def get_flood_map(id: int):
    raise HTTPException(status_code=501, detail="Not implemented")
