from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from . import types


class AccountBase(BaseModel):
    id: int

    class Config:
        orm_mode = True


class EventBase(BaseModel):
    id: int

    class Config:
        orm_mode = True


class Account(AccountBase):
    participant_events: List[EventBase] = []

    class Config:
        orm_mode = True


class Event(EventBase):
    title: str
    is_private: bool
    location_id: int
    category_id: int
    intensity: types.Intensity
    create_time: datetime
    start_time: datetime
    end_time: datetime
    max_participant_count: int
    creator_account_id: int
    description: Optional[str]
    participant_ids: List[int] = []
    bookmarked: bool

    class Config:
        orm_mode = True


class Account_Event_with_Count(BaseModel):
    data: List[Event] = []
    total_count: int

    class Config:
        orm_mode = True
