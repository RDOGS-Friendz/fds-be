from typing import Sequence, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Request
from dataclasses import dataclass
from pydantic import BaseModel

import database as db
from base import do
from middleware.dependencies import get_token_header


router = APIRouter(
    tags=['Profile'],
    dependencies=[Depends(get_token_header)],
)


class AddProfileInput(BaseModel):
    tagline: str
    department_id: Optional[int]
    social_media_link: Optional[str]
    birthday: Optional[datetime]
    about: Optional[str]


@router.post("/account/{account_id}/profile")
async def add_profile_under_account(account_id: int, data: AddProfileInput, request: Request) -> do.AddOutput:
    """
    ### Auth
    - Self
    """
    if request.state.id is not account_id:
        raise HTTPException(status_code=400, detail="No Permission")
    profile_id = await db.profile.add_under_account(account_id=account_id, tagline=data.tagline, department_id=data.department_id,
                                                    social_media_link=data.social_media_link, birthday=data.birthday, about=data.about)
    return do.AddOutput(id=profile_id)


# WIP: category related
@router.get("/account/{account_id}/profile")
async def read_profile_under_account(account_id: int, request: Request) -> do.Profile:
    return await db.profile.read_under_account(account_id=account_id)
