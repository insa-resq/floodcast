from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel

from app.dependencies.config import Config
from app.predict.predict_flow_rate import predict_flow_rate

app = FastAPI()


@app.get("/")
async def root(config: Config):
    return {
        "message": "Hello from flow-prediction service!",
        "config": config.model_dump(),
    }


class FlowPredictionResult(BaseModel):
    value: float


@app.get("/flow")
async def get_predicted_flow_rate(
    config: Config, prediction_time: datetime
) -> FlowPredictionResult:
    """
    Returns predicted flow rate in m3/s at prediction_time
    """
    return FlowPredictionResult(
        value=await predict_flow_rate(
            prediction_time.replace(minute=0, second=0, microsecond=0, tzinfo=None)
        )
        / 3600
    )
