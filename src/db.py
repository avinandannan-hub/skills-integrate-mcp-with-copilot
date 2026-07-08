
from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

DB_PATH = Path(__file__).parent / 'activities.db'
DATABASE_URL = f'sqlite:///{DB_PATH}'
engine = create_engine(DATABASE_URL, echo=False)


def init_db():
    if not DB_PATH.exists():
        SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)
