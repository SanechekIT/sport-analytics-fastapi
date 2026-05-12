from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from app.models.base_entry import BaseEntry

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.meal_item import MealItem



class Meal(BaseEntry, table=True):   # ← наследуемся от BaseEntry
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    # user_id и created_at/updated_at теперь приходят из BaseEntry
    # поле date удаляем, если оно дублирует created_at
    # если date нужна для другого – оставляем
    user: Optional["User"] = Relationship(back_populates="meals")
    items: List["MealItem"] = Relationship(...)
