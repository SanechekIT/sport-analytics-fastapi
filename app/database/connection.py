from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sport.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

def get_db():
    """
    Создает и предоставляет сессию базы данных.
    После завершения работы автоматически закрывает сессию.

    Yields:
        Session: Сессия SQLModel для работы с базой данных
    """
    with Session(engine) as session:
        yield session