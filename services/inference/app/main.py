import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from httpx import AsyncClient

from app.db.models import Prediction
from app.db.repo import DB
from app.dependencies.config import Config, get_config
from app.dependencies.db import DBDependency, get_db
from app.models.prediction import PredictionModel


async def fetch_prediction() -> Prediction:
    url = "http://flood-prediction-service:8000/?"
    async with AsyncClient() as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()
        return Prediction(**data)


async def send_alert(prediction: Prediction):
    url = "http://alert-service:8000/alertUsers"
    async with AsyncClient() as client:
        r = await client.post(url, data={"data": prediction})
        r.raise_for_status()


async def run_inference(db: DB):
    while True:
        try:
            # Call flood prediction service
            prediction = await fetch_prediction()

            # Add to database
            db.add_prediction(prediction)

            # Call alert service
            await send_alert(prediction)
        except Exception as e:
            print(f"Job failed: {e}")
        await asyncio.sleep(60 * 60)  # 1 hour


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = await get_config()
    db = get_db(config)
    # run once on startup
    asyncio.create_task(run_inference(db))
    yield
    # optional: cleanup on shutdown


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root(config: Config):
    return {"message": "Hello from inference service!", "config": config}


@app.get("/predictions")
def get_predictions(db: DBDependency) -> list[PredictionModel]:
    return list(map(PredictionModel.model_validate, db.get_all_predictions()))

@app.get("/predictions/{id}")
def get_predictions(db: DBDependency) -> PredictionModel:
    prediction = db.get_prediction_by_id(id)
    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return PredictionModel.model_validate(prediction)

@app.post("/test")
def add_test_prediction(db: DBDependency):
    db.add_prediction(
        Prediction(
            severity=1.0,
            probability=1.0,
            start_date=datetime.now(),
            end_date=datetime.now(),
        )
    )
