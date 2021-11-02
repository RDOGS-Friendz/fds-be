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


@dataclass
class ReadProfileOutput:
    account_id: int
    tagline: str
    department: str
    social_media_acct: str
    birthday: datetime
    preferred_category_id: Sequence[int]
    about: str


# WIP: category related
@router.get("/account/{account_id}/profile")
async def read_account_profile(account_id: int, request: Request) -> ReadProfileOutput:
    """
    ### Auth
    - ALL
    """
    try:
        await db.account.read(account_id=request.state.id)
    except:
        raise HTTPException(status_code=400, detail="No Permission")

    profile = await db.profile.read_under_account(account_id=account_id)
    account_categories = await db.account_category.browse_account_categories(account_id=account_id)
    department = await db.department.read(department_id=profile.department_id)
    return ReadProfileOutput(account_id=profile.account_id, tagline=profile.tagline, department=department.department_name,
                             social_media_acct=profile.social_media_link, birthday=profile.birthday,
                             preferred_category_id=[result.category_id for result in account_categories],
                             about=profile.about)
