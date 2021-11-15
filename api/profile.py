import pydantic
from typing import Sequence, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Request
from dataclasses import dataclass
from pydantic import BaseModel

import database as db
from base import do, enum
from middleware.dependencies import get_token_header
from middleware.response import SuccessResponse


router = APIRouter(
    tags=['Profile'],
    dependencies=[Depends(get_token_header)],
)


@dataclass
class ReadProfileOutput:
    account_id: int
    real_name: Optional[str]
    gender: enum.GenderType

    # profile
    tagline: Optional[str]
    department: Optional[str]
    social_media_acct: Optional[str]
    birthday: Optional[str]
    preferred_category_id: Optional[Sequence[int]]
    about: Optional[str]


@router.get("/account/{account_id}/profile", response_model=ReadProfileOutput)
async def read_account_profile(account_id: int, request: Request) -> ReadProfileOutput:
    """
    ### Auth
    - ALL
    - Self (private info)
    """

    is_self = request.state.id is account_id

    account = await db.account.read(account_id=account_id)
    profile = await db.profile.read_under_account(account_id=account_id)
    account_categories = await db.account_category.browse_account_categories(account_id=account_id)
    department = await db.department.read(department_id=profile.department_id)
    return ReadProfileOutput(account_id=profile.account_id,
                             real_name=account.real_name if (is_self or not account.is_real_name_private) else None,
                             gender=account.gender,
                             tagline=profile.tagline,
                             department=department.department_name,
                             social_media_acct=profile.social_media_link,
                             birthday=profile.birthday if (is_self or not profile.is_birthday_private) else None,
                             preferred_category_id=[result.category_id for result in account_categories],
                             about=profile.about)


class EditProfileInput(BaseModel):
    tagline: str = None
    department: str = None
    social_media_acct: str = None
    birthday: datetime = None
    preferred_category_id: Sequence[int] = None
    about: str = None


@router.patch("/account/{account_id}/profile")
async def edit_account_profile(account_id: int, data: EditProfileInput, request: Request):
    """
    ### Auth
    - Self
    """
    if request.state.id is not account_id:
        raise HTTPException(status_code=400, detail="No Permission")

    preferred_category_ids = pydantic.parse_obj_as(list[int], data.preferred_category_id)

    await db.profile.edit_under_account(account_id=account_id,
                                        tagline=data.tagline,
                                        department_name=data.department,
                                        social_media_link=data.social_media_acct,
                                        birthday=data.birthday,
                                        preferred_category_ids=preferred_category_ids,
                                        about=data.about)
    return SuccessResponse()
