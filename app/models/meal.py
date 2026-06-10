from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from app.models.base_entry import BaseEntry

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.meal_item import MealItem

class Meal(BaseEntry, table=True):
    __tablename__ = "meals"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    date: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    user: Optional["User"] = Relationship(back_populates="meals")
    items: List["MealItem"] = Relationship(
        back_populates="meal",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    
    proteins: float = Field(default=0.0, ge=0, description="Total proteins in grams")
    fats: float = Field(default=0.0, ge=0, description="Total fats in grams")
    carbs: float = Field(default=0.0, ge=0, description="Total carbohydrates in grams")
    portion: Optional[float] = Field(default=None, ge=0, description="Portion size (e.g., in grams or ml)")

