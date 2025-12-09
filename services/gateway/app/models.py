from pydantic import BaseModel, AfterValidator, Field
from datetime import datetime, timedelta
from typing import Annotated

class User(BaseModel):
    name: str
    mail: str
    ip: str
    departements: list[int]

class Segment(BaseModel):
    id: int
    lat_1: float
    long_1: float
    lat_2: float
    long_2: float

class Flood(BaseModel):
    id: int
    segments_ids: list[int]
    severity: int
    probability: float
    period: AvailabilityPeriod

def validate_hour_datetime(v: datetime) -> datetime:
    if v.minute or v.second or v.microsecond:
        raise ValueError("datetime must be on the hour")
    return v

HourDatetime = Annotated[datetime, AfterValidator(validate_hour_datetime)]

def validate_hour_timedelta(v: timedelta) -> timedelta:
    if v.total_seconds() % 3600 != 0:
        raise ValueError("timedelta must be a whole number of hours")
    return v

HourDelta = Annotated[timedelta, AfterValidator(validate_hour_timedelta)]

class AvailabilityPeriod(BaseModel):
    start: HourDatetime = Field(
        title="A datetime with one hour resolution.",
        examples=[datetime(2025, 9, 9, 12)],
    )
    span: HourDelta = Field(
        title="A timedelta with one hour resolution.", examples=[timedelta(hours=1)]
    )
