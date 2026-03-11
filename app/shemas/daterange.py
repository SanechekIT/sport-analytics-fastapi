from pydantic import BaseModel
from datetime import date, datetime
from typing import List
from .meal_item import MealItemCreate, MealItem  # импортирую то, что сделаем дальше

class DateRange(BaseModel):
    start_date: datetime
    end_date: datetime

class DailySummery(BaseModel):
    date: date
    total_calories: float = 0
    total_proteins: float = 0
    total_fats: float = 0
    total_carbs: float = 0
    meals_count: int = 0

