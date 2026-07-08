
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class Participant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    activity_id: int = Field(foreign_key='activity.id')
    activity: Optional['Activity'] = Relationship(back_populates='participants')


class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str
    schedule: str
    max_participants: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    participants: List[Participant] = Relationship(back_populates='activity')
