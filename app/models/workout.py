from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Workout(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    date: Optional[datetime] = None  # или datetime = Field(default_factory=datetime.now)
    user_id: int = Field(foreign_key="user.id")