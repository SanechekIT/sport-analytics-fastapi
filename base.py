from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class BaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={
            "server_default": "CURRENT_TIMESTAMP"
        }
    )
    
    updated_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        sa_column_kwargs={
            "onupdate": datetime.utcnow
        }
    )
    
    is_deleted: bool = Field(default=False, nullable=False)
    
    def touch(self) -> None:
        self.updated_at = datetime.utcnow()
