from typing import Sequence, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from databases import Database
from dataclasses import dataclass
from pydantic import BaseModel

from base import do, enum
import database as db
from config import jwt_config

router = APIRouter(tags=['Friend'])

@router.get("/account/{account_id}/friends")
async def read_account_friends(account_id: int):
    return await db.friend.get_account_friends(account_id=account_id)


# class AddProfileInput(BaseModel):
#     tagline: str
#     department_id: Optional[int]
#     social_media_link: Optional[str]
#     birthday: Optional[datetime]
#     about: Optional[str]


# @router.post("/account/{account_id}/profile")
# async def add_profile_under_account(account_id: int, data: AddProfileInput) -> do.AddOutput:
#     profile_id = await db.profile.add_under_account(account_id=account_id, tagline=data.tagline, department_id=data.department_id,
#                                                     social_media_link=data.social_media_link, birthday=data.birthday, about=data.about)
#     return do.AddOutput(id=profile_id)


# # WIP: category related
# @router.get("/account/{account_id}/profile")
# async def read_profile_under_account(account_id: int) -> do.Profile:
#     return await db.profile.read_under_account(account_id=account_id)
