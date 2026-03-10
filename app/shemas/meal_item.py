from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Базовая схема
class MealItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    calories: int
    protein: float
    fat: float
    carbohydrates: float

# Для создания
class MealItemCreate(MealItemBase):
    pass

# Для обновления
class MealItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    calories: Optional[int] = None
    protein: Optional[float] = None
    fat: Optional[float] = None
    carbohydrates: Optional[float] = None

# Для ответа
class MealItem(MealItemBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True  # вместо orm_mode
