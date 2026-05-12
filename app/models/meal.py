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
    date: datetime = Field(default_factory=datetime.utcnow)  # ← дата приёма пищи, оставляем
    # user_id удалён (есть в BaseEntry)
    # created_at и updated_at удалены (есть в BaseEntry)

    user: Optional["User"] = Relationship(back_populates="meals")
    items: List["MealItem"] = Relationship(
        back_populates="meal",
        cascade="all, delete-orphan"
    )
