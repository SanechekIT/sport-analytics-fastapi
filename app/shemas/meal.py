from pydantic import BaseModel
from datetime import date, datetime
from typing import List
from .meal_item import MealItemCreate, MealItem  # импортирую то, что сделаем дальше

class MealBase(BaseModel):
    meal_type: str  # breakfast, lunch, dinner, snack
    date: date

class MealCreate(MealBase):
    items: List[MealItemCreate]  # список продуктов, которые съели

class Meal(MealBase):
    id: int
    user_id: int
    created_at: datetime
    items: List[MealItem]  # продукты с посчитанными КБЖУ
    total_calories: float  

class MealUpdate(BaseModel):
    meal_type: str | None = None
    date: date | None = None
    items: List[MealItemCreate] | None = None  # если меняем состав
