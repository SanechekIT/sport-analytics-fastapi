from sqlmodel import SQLModel, Field
from typing import Optional

class Product(SQLModel):
    __tablename__ = "products" 
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200, index=True)
    calories_per_100g: Optional[int] = Field(default=None, ge=0)
   
