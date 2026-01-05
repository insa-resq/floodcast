from typing import Annotated

from fastapi import FastAPI, Query

from app.fetch import FlowQueryParams, FlowResponse, fetch_flows

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello from flow-data service!"}


@app.get("/data")
async def get_data(query: Annotated[FlowQueryParams, Query()]) -> FlowResponse:
    return await fetch_flows(query)
