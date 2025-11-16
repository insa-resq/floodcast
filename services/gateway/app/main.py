from fastapi import FastAPI
import httpx

app = FastAPI()

@app.get("/")
async def root():
    async with httpx.AsyncClient() as client:
        r = await client.get("http://weather-data-service:8000")
        return {"message": "Hello from gateway service!", "weather": r.json()}

