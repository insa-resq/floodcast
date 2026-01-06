from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Prediction(Base):
    __tablename__ = "prediction"
    id: Mapped[int] = mapped_column(primary_key=True)

    # Use single segment for now
    segment_id: Mapped[int] = mapped_column(default=0)

    severity: Mapped[float] = mapped_column()

    probability: Mapped[float] = mapped_column()

    start_date: Mapped[datetime] = mapped_column()

    end_date: Mapped[datetime] = mapped_column()

    def __repr__(self) -> str:
        return f"Prediction(id={self.id!r})"
