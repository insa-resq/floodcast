from fastapi import FastAPI, HTTPException
from typing import List

from app.dependencies.config import Config
from app.dependencies.db import DBDependency
from app.db.models import User
from app.models.user import UserModel
from app.models.prediction import PredictionModel
import httpx
app = FastAPI()


# --------------------------------------------------
# Utils (mock alerting functions)
# --------------------------------------------------

def mailto(email: str, prediction: PredictionModel):
    print(f"[MAIL] Alerte envoyée à {email} : {prediction}")





async def send_to_ip(ip: str, prediction: PredictionModel):
    """
    Send alert to a remote service identified by its IP.
    """
    url = f"http://{ip}:8000/alert"

    payload = prediction.model_dump()

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

        print(f"[IP] Alerte envoyée à {ip}")

    except httpx.RequestError as e:
        print(f"[IP][ERROR] Impossible de joindre {ip}: {e}")

    except httpx.HTTPStatusError as e:
        print(
            f"[IP][ERROR] {ip} a répondu {e.response.status_code} "
            f"- {e.response.text}"
        )



# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.get("/")
async def root(config: Config):
    return {
        "message": "Hello from alert service!",
        "log_level": config.log_level,
    }


@app.get("/users", response_model=List[UserModel])
def get_users(db: DBDependency):
    return db.get_all_users()


@app.post("/subscribe", status_code=201)
def subscribe_user(user: UserModel, db: DBDependency):
    db.add_user(User(**user.model_dump()))
    return {"status": "subscribed"}


@app.post("/alertUsers")
def alert_users(
    prediction: PredictionModel,
    db: DBDependency,
):
    """
    Envoie une alerte si la prédiction correspond à une crue
    """
    CRUE_SEVERITY_THRESHOLD = 0.7

    if prediction.severity < CRUE_SEVERITY_THRESHOLD:
        return {"status": "no alert", "reason": "severity too low"}

    users = db.get_all_users()

    if not users:
        raise HTTPException(status_code=404, detail="No users to alert")

    for user in users:
        if user.mail:
            mailto(user.mail, prediction)
        if user.ip:
            send_to_ip(user.ip, prediction)

    return {
        "status": "alert sent",
        "users_notified": len(users),
        "severity": prediction.severity,
    }
