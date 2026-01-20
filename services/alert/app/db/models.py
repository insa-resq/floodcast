from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column()

    mail: Mapped[str] = mapped_column()

    ip: Mapped[str] = mapped_column()

    #segments_ids: Mapped[list[int]] = mapped_column()

    #departements: Mapped[list[int]] = mapped_column()

    def __repr__(self) -> str:
        return f"User(id={self.id!r})"
