from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    calories: Optional[int] = None
    proteins: Optional[float] = None
    fats: Optional[float] = None
    carbs: Optional[float] = None
    category: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
