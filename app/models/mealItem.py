from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class MealItem(SQLModel,table=True): 
    __tablename__ = "meal_items" 

    id: Optional[int] = Field(default=None, primary_key=True)  
    meal_id: int = Field(foreign_key="meals.id", index=True)  
    product_id: int = Field(foreign_key="products.id", index=True)  
    grams: float = Field(gt=0) 
