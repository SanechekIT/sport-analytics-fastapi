from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class MealItem(SQLModel): 
    __tablename__ = "meal_items" 

    id: Optional[int] = Field(default=None, primary_key=True)  
    meal_id: int = Field(foreign_key="meals.id", index=True)  
    product_id: int = Field(foreign_key="product_models.id", index=True)  
    grams: float = Field(gt=0) 
