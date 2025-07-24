from database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class People(Base):
    __tablename__ = 'people'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    mother_id: Mapped[int | None] = mapped_column(ForeignKey('people.id'), nullable=True)
    father_id: Mapped[int | None] = mapped_column(ForeignKey('people.id'), nullable=True)


    def __repr__(self):
        return (
            f"People(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, mother_id"
            f"={self.mother_id}, "
            f"father_id={self.father_id}")
