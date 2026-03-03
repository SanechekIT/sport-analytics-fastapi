from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class MealItem(SQLModel):  # ✅ MealItem (с большой буквы, Item, а не item)
    __tablename__ = "meal_items"  # ✅ множественное число, правильное название

    id: Optional[int] = Field(default=None, primary_key=True)  # ✅ ОДИН primary_key
    meal_id: int = Field(foreign_key="meals.id", index=True)   # ✅ meals.id (как в Meal)
    product_id: int = Field(foreign_key="products.id", index=True)  # ✅ products.id
    grams: float = Field(gt=0)  # Количество в граммах
