from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.meal import Meal
    from app.models.product import Product


class MealItem(SQLModel, table=True):
    __tablename__ = "meal_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    meal_id: int = Field(foreign_key="meals.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: float = Field(description="Вес в граммах")
    serving_size: float = Field(default=100, description="Размер порции")

    # Relationship импортирован из sqlmodel
 
    meal: Optional["Meal"] = Relationship(back_populates="items")
    product: Optional["Product"] = Relationship(back_populates="meal_items")
