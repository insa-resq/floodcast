from fastapi import FastAPI, HTTPException
import yaml
import os

app = FastAPI()

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "../config-repo")

@app.get("/config/{service_name}")
async def get_config(service_name: str):
    filename = f"{service_name}.yml"
    filepath = os.path.join(CONFIG_DIR, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Config not found")

    with open(filepath, "r") as f:
        config = yaml.safe_load(f)

    return {"service": service_name, "config": config}

