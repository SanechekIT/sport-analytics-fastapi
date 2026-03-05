from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.meal_item import MealItem


class Product(SQLModel, table=True):
    __tablename__ = "products"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    calories: float
    proteins: float
    fats: float
    carbs: float
    is_available: bool = Field(default=True)

    # ДОБАВЛЕНО: связь с MealItem
    meal_items: List["MealItem"] = Relationship(back_populates="product")
