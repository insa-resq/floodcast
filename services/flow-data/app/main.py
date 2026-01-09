from datetime import date, timedelta
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from app.fetch import (
    FlowInfo,
    FlowQueryParams,
    FlowResponse,
    fetch_flows,
    latest_measure,
)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello from flow-data service!"}


@app.get("/measurements")
async def get_data(query: Annotated[FlowQueryParams, Query()]) -> FlowResponse:
    return await fetch_flows(query)


class LatestFlowQueryParams(BaseModel):
    latitude: float
    longitude: float
    max_distance: int


@app.get("/measurements/flow/latest")
async def get_latest_flow(query: Annotated[LatestFlowQueryParams, Query()]) -> FlowInfo:
    res = await fetch_flows(
        FlowQueryParams(
            latitude=query.latitude,
            longitude=query.longitude,
            max_distance=query.max_distance,
            start_date=date.today() - timedelta(days=1),
        )
    )
    latest = latest_measure(res, measure="Q", measure_type="max", span="daily")
    if latest is None:
        raise HTTPException(
            404, "Yesterday's max flow rate not found for this location."
        )
    return latest
