from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PredictionModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    segment_id: int
    severity: float
    probability: float
    start_date: datetime
    end_date: datetime
