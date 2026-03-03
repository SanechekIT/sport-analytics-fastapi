from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Mealitem(SQLMeal):
    __tablenames__ = "mealitem"

    id: Optional[int] = Field(default = None,primary_key=True)
    meal_id: int = Field(foreign_key="meal.id", index=True)
    product_id: int = Field(default=None,primary_key=True)
    grams: float = Field(gt=0) 

