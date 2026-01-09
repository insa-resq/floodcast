from app.db.models import User
from sqlalchemy import Engine, select
from sqlalchemy.orm import sessionmaker


class DB:
    session: sessionmaker

    def __init__(self, engine: Engine) -> None:
        self.session = sessionmaker(engine, expire_on_commit=False)

    def add_user(self, user: User):
        with self.session.begin() as session:
            session.add(user)

    def get_all_users(self) -> list[User]:
        with self.session.begin() as session:
            return session.scalars(select(User)).all()
        
    def get_all_users_from_dep(self, dep) -> list[User]:
        with self.session.begin() as session:
            return session.scalars(select(User)).all()
        
    def get_user_by_id(self) -> list[User]:
        with self.session.begin() as session:
            return session.scalars(select(User)).all()
