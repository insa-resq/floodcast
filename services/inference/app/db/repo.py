from sqlalchemy import Engine, select
from sqlalchemy.orm import sessionmaker

from app.db.models import Prediction


class DB:
    session: sessionmaker

    def __init__(self, engine: Engine) -> None:
        self.session = sessionmaker(engine, expire_on_commit=False)

    def add_prediction(self, prediction: Prediction):
        with self.session.begin() as session:
            session.add(prediction)

    def get_all_predictions(self) -> list[Prediction]:
        with self.session.begin() as session:
            return session.scalars(select(Prediction)).all()

    def get_prediction_by_id(self, id: int) -> Prediction:
        with self.session.begin() as session:
            return session.scalars(
                select(Prediction).where(Prediction.id == id)
            ).first()
