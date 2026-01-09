from datetime import datetime, timedelta

from fastapi import FastAPI

from app.dependencies.config import Config
from app.predict.watershed import watershed_dataset
from app.predict.weather import AvailabilityPeriod, rainfall_data

app = FastAPI()


@app.get("/")
async def root(config: Config):
    with watershed_dataset() as watershed:
        async with rainfall_data(
            AvailabilityPeriod(
                start=datetime(year=2025, month=9, day=1, hour=1),
                span=timedelta(hours=1),
            )
        ) as rain:
            return {
                "message": "Hello from flow-prediction service!",
                "config": config.model_dump(),
                "watershed": watershed.index(0, 0),
                "rain": rain.index(0, 0),
            }
