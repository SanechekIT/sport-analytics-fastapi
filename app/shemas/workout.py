from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class WorkoutBase(SQLModel):
    name:str
    date:datetime
    duration_minutes:int
    notes:str

class WorkoutCreate(WorkoutBase):
    pass #Пустой,тк наследует все поля из Base

class Workout(WorkoutBase,table = True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(fpreign_key = "user.id")
