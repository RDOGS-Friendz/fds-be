from dataclasses import dataclass
from datetime import datetime
from typing import Sequence, Optional
from api import include_routers

from base import enum


"""
Database Output: return every column of a table in database
"""


@dataclass
class AddOutput:
    id: int


@dataclass
class FriendOutput:
    friend_account_id: list


@dataclass
class FriendRequestOutput:
    friend_request_id: list


@dataclass
class Account:
    id: int
    username: str
    pass_hash: str
    real_name: str
    email: str
    gender: enum.GenderType
    joined_date: datetime
    is_real_name_private: bool
    is_superuser: bool
    is_deleted: bool


@dataclass
class Profile:
    id: int
    account_id: int
    is_birthday_private: bool
    tagline: str
    department_id: int
    social_media_link: str
    birthday: str
    about: str


@dataclass
class Friendship:
    requester_id: int
    addressee_id: int
    status: enum.FriendshipType


@dataclass
class AccountCategory:
    account_id: int
    category_id: int


@dataclass
class Department:
    id: int
    school: str
    department_name: str


@dataclass
class Category:
    id: int
    name: str

@dataclass
class CategoryOutput:
    categories: Sequence[Category]

@dataclass
class Location:
    id: int
    name: str
    type: enum.LocationType
    lat: Optional[float]
    lng: Optional[float]

@dataclass
class LocationsOutput:
    locations: Sequence[Location]

@dataclass
class Event:
    id: int
    title: str
    is_private: bool
    location_id: int
    category_id: int
    intensity: enum.IntensityType
    create_time: str
    start_time: str
    end_time: str
    max_participant_count: int
    creator_account_id: int
    description: str


@dataclass
class EventView:
    id: int
    title: str
    is_private: bool
    location_id: int
    category_id: int
    intensity: enum.IntensityType
    create_time: str
    start_time: str
    end_time: str
    max_participant_count: int
    creator_account_id: int
    description: str
    participant_ids: Sequence[int]
    bookmarked: bool


@dataclass
class EventBookmark:
    id: int
    account_id: int
    event_id: int

@dataclass
class EventsIdOutput:
    event_ids: Sequence[int]

@dataclass
class Reaction:
    id: int
    event_id: int
    content: str
    author_id: int

@dataclass
class ReactionsOutput:
    reactions: Sequence[Reaction]
