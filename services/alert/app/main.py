from fastapi import FastAPI

from app.dependencies.config import Config
from models.user import UserModel
from models.prediction import PredictionModel
from dependencies.db import DBDependency

app = FastAPI()


@app.get("/")
async def root(config: Config):
    return {"message": "Hello from alert service!", "config": config}


@app.get("/users")
def get_users(db: DBDependency) -> list[UserModel]:
    return list(map(PredictionModel.model_validate, db.get_all_users()))


@app.get("/users")
def get_users_from_dep(db: DBDependency, dep: int) -> list[UserModel]:
    return list(map(PredictionModel.model_validate, db.get_all_users_from_dep(dep)))


@app.post("/subscribe")
def add_test_prediction(db: DBDependency, user: UserModel):
    db.add_user(user)


@app.post("/alert")
def alert(user: UserModel, prediction: PredictionModel):
    pass
    mail = user.mail
    ip = user.ip
    if mail!="":
        mailto(user.mail, prediction)
        send_to_ip(user.ip, prediction)


    