import pydantic
import asyncpg
from typing import Sequence, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Request
from dataclasses import dataclass
from pydantic import BaseModel

from base import do, enum, security
import database as db
from middleware.dependencies import get_token_header

router = APIRouter(
    tags=['Account'],
    dependencies=[Depends(get_token_header)],
)


class LoginInput(BaseModel):
    username: str
    password: str


@dataclass
class LoginOutput:
    auth_token: str
    account_id: int


@router.post("/jwt")
async def login(data: LoginInput) -> Sequence[do.Account]:
    account = await db.account.read_by_username(username=data.username)
    if not security.verify_password(to_test=data.password, hashed=account.pass_hash):
        raise HTTPException(status_code=400, detail="Login Failed")

    login_token = security.encode_jwt(account_id=account.id)

    return LoginOutput(auth_token=login_token, account_id=account.id)


class AddAccountInput(BaseModel):
    username: str
    password: str
    real_name: str
    email: str
    gender: enum.GenderType
    is_superuser: Optional[bool] = False

    # profile
    tagline: Optional[str] = ''
    department_id: Optional[int] = None
    social_media_link: Optional[str] = ''
    birthday: Optional[datetime] = None
    about: Optional[str] = ''


@router.post("/account")
async def add_account(data: AddAccountInput) -> do.AddOutput:
    try:
        account_id = await db.account.add(username=data.username, pass_hash=security.hash_password(password=data.password),
                                          real_name=data.real_name, email=data.email, gender=data.gender, is_superuser=data.is_superuser)
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=400, detail="Username Exists")

    await db.profile.add_under_account(account_id=account_id, tagline=data.tagline, department_id=data.department_id,
                                       social_media_link=data.social_media_link, birthday=data.birthday, about=data.about)
    return do.AddOutput(id=account_id)


@dataclass
class BrowseAccountOutput:
    account_id: int
    username: str
    real_name: str


@router.get("/account")
async def browse_account(request: Request, search: str = '') -> Sequence[do.Account]:

    result = await db.account.browse_by_search(to_search=search)
    return [BrowseAccountOutput(account_id=account.id,
                                username=account.username,
                                real_name=account.real_name)
            for account in result]


@router.get("/account/batch")
async def batch_get_account(account_ids: pydantic.Json, request: Request) -> Sequence[do.Account]:
    account_ids = pydantic.parse_obj_as(list[int], account_ids)
    if not account_ids:
        return []
    result = await db.account.batch_read_by_ids(account_ids=account_ids)
    return [BrowseAccountOutput(account_id=account.id,
                                username=account.username,
                                real_name=account.real_name)
            for account in result]


class EditAccountPrivacyInput(BaseModel):
    display_real_name: bool = None
    display_birthday: bool = None


@router.patch("/account/{account_id}/privacy")
async def edit_account_privacy(account_id: int, data: EditAccountPrivacyInput, request: Request) -> int:
    await db.account.edit_privacy(account_id=account_id, is_real_name_private=(not data.display_real_name))
    await db.profile.edit_privacy(account_id=account_id, is_birthday_private=(not data.display_birthday))
