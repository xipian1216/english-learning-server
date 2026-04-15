import os
from pathlib import Path
import sys

from sqlmodel import Field, Session, SQLModel, create_engine

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: int | None = None


hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)


database_url = os.getenv("DATABASE_URL", "postgresql+psycopg://username:password@localhost:5432/testdb")
engine = create_engine(database_url)


SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    session.add(hero_1)
    session.add(hero_2)
    session.add(hero_3)
    session.commit()


if __name__ == "__main__":
    print("PostgreSQL connection test passed.")
