from pydantic import BaseModel
from datetime import datetime

class ProductBase(BaseModel):
    name:str
    calories:float
    proteins:float
    fats:float
    carbs:float

class ProductCreate(ProductBase):
   pass

class Product(ProductBase):
    id: int
    user_id: int
    created_at: datetime

class ProductUpdate(BaseModel):
    name: str | None = None
    calories: float | None = None
    proteins: float | None = None
    fats: float | None = None
    carbs: float | None = None
