from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.user import User
    from app.models.meal_item import MealItem


class Meal(SQLModel, table=True):
    __tablename__ = "meals"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    date: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="users.id")


    user: Optional["User"] = Relationship(back_populates="meals")
    items: List["MealItem"] = Relationship(
        back_populates="meal",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
