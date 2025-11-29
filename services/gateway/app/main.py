from fastapi import FastAPI
import httpx
import asyncio
import logging

app = FastAPI()
logger = logging.getLogger("gateway")

config: dict = {}

CONFIG_SERVER_URL = "http://config-server:8000/config/gateway"


async def fetch_config_with_retry(
    max_retries: int = 10,
    delay_seconds: float = 2.0,
) -> dict:
    """
    Essaie de récupérer la config auprès du config-server avec plusieurs tentatives.
    Si toutes échouent, renvoie une config par défaut.
    """
    last_exc = None

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"[gateway] Attempt {attempt} to load config from {CONFIG_SERVER_URL}")
            async with httpx.AsyncClient() as client:
                r = await client.get(CONFIG_SERVER_URL, timeout=5.0)
                r.raise_for_status()
                body = r.json()
                cfg = body.get("config")
                if cfg is None:
                    raise ValueError(f"No 'config' key in response: {body}")
                logger.info(f"[gateway] Successfully loaded config: {cfg}")
                return cfg
        except Exception as e:
            last_exc = e
            logger.warning(f"[gateway] Failed to load config (attempt {attempt}/{max_retries}): {e}")
            await asyncio.sleep(delay_seconds)

    logger.error(f"[gateway] Could not reach config-server after {max_retries} attempts: {last_exc}")
    # Config par défaut pour ne pas crasher
    return {
        "service_name": "gateway",
        "routes": {
            "weather_api": {"url": "http://weather-data-service:8000"},
            "flow_api": {"url": "http://flow-data-service:8000"},
        },
        "port": 8000,
        "log_level": "warning",
    }


@app.on_event("startup")
async def startup_event():
    global config
    config = await fetch_config_with_retry()
    print("Gateway config loaded:", config)


@app.get("/")
async def root():
    # appel du microservice météo pour vérifier que tout marche
    weather_url = config["routes"]["weather_api"]["url"]
    async with httpx.AsyncClient() as client:
        r = await client.get(weather_url)
        weather = r.json()

    return {
        "message": "Hello from gateway service!",
        "config": config,
        "weather": weather,
    }
