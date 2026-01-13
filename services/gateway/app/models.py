from pydantic import BaseModel
from datetime import datetime

class UserModel(BaseModel):
    name: str
    mail: str
    ip: str
    #segments_ids: list[int]
    #departements: list[int]

class Segment(BaseModel):
    id: int
    lat_1: float
    long_1: float
    lat_2: float
    long_2: float

class PredictionModel(BaseModel):
    id: int
    segments_ids: list[int]
    severity: float
    probability: float
    start_date: datetime
    end_date: datetime
