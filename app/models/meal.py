from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Meal(SQLModel):
    __tablename__ = "meals"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    date: datetime = Field(index=True)
    meal_type: str = Field(max_length=50)
    created_at: datetime = Field(default_factory=datetime.now)
    description: Optional[str] = Field(default=None, max_length=500)
    calories: Optional[int] = Field(default=None, ge=0, le=10000)
