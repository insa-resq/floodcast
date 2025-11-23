import httpx
from fastapi import FastAPI

app = FastAPI()

async def get_config():
    async with httpx.AsyncClient() as client:
        r = await client.get("http://config-server:8000/config/weather-data")
        return r.json()["config"]

config = None

@app.on_event("startup")
async def load_config():
    global config
    config = await get_config()
    print("Loaded config:", config)

@app.get("/")
async def root():
    return {"message": "weather data OK", "config": config}

