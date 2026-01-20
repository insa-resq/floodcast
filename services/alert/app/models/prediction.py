from datetime import datetime
from pydantic import BaseModel


class PredictionModel(BaseModel):
    id: int
    segment_id: int
    severity: float
    probability: float
    start_date: datetime
    end_date: datetime
