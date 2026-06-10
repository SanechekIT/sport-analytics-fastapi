from datetime import datetime, date
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from app.models.base_entry import BaseEntry

if TYPE_CHECKING:
    from app.models.user import User


class Prediction(BaseEntry, table=True):
    __tablename__ = "predictions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    target_date: date
    predicted_weight_kg: float = Field(gt=0, description="Предсказанный вес в кг")
    confidence_low: float = Field(gt=0, description="Нижняя граница доверительного интервала")
    confidence_high: float = Field(gt=0, description="Верхняя граница доверительного интервала")
    based_on_data_until: date
    is_overridden: bool = Field(default=False)
    actual_weight_kg: Optional[float] = Field(default=None, gt=0, description="Реальный вес (заполняется постфактум)")

    # Связь с пользователем (позже добавишь в User: predictions: List["Prediction"] = Relationship(back_populates="user"))
    user: Optional["User"] = Relationship(back_populates="predictions")
