from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

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
    birthday: datetime
    about: str

@dataclass
class Friendship:
    requester_id: int
    addressee_id: int
    status: enum.FriendshipType
@dataclass
class Category:
    id: int
    name: str
@dataclass
class CategoryOutput:
    categories: Sequence[Category]