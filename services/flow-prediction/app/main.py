from fastapi import FastAPI

from app.dependencies.config import Config
from app.predict.watershed import watershed_dataset

app = FastAPI()


@app.get("/")
async def root(config: Config):
    with watershed_dataset() as ds:
        return {
            "message": "Hello from flow-prediction service!",
            "config": config.model_dump(),
            "ds": ds.index(0, 0),
        }
