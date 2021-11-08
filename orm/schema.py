from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from . import types


# class Event(BaseModel):
#     id: int
#     title: str
#     is_private: bool
#     location_id: int
#     category_id: int
#     intensity: types.Intensity
#     create_time: datetime
#     start_time: datetime
#     end_time: datetime
#     max_participant_count: int
#     creator_account_id: int
#     description: Optional[str]
#     participant_accounts: List[Account] = []
#
#     class Config:
#         orm_mode = True


class Account(BaseModel):
    id: int
    # participant_events: List[Event] = []

    class Config:
        orm_mode = True


class Event(BaseModel):
    id: int
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
    # participant_accounts: List[Account] = []

    class Config:
        orm_mode = True
