from fastapi import FastAPI
import httpx
import logging

# from app.dependencies.config import Config
from app.dependencies.config import Config

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
