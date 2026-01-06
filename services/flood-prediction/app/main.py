from fastapi import FastAPI

from app.dependencies.config import Config

app = FastAPI()


@app.get("/")
async def root(config: Config):
    return {"message": "Hello from flood prediction service!", "config": config}
