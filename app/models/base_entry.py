from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class BaseEntry(SQLModel):
    class Config:
        abstract = True

class Prediction(BaseEntry, table=True):
        __tablename__ = "predictions"

        id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
