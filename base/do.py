from dataclasses import dataclass
from datetime import datetime

from base import enum


"""
Database Output: return every column of a table in database
"""


@dataclass
class AddOutput:
    id: int


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
    socila_media_link: str
    birthday: datetime
    about: str
