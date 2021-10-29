from typing import Sequence, Optional

from fastapi import HTTPException

from main import database
from base import do, enum


async def add_under_account(account_id: int,
                            tagline: str,
                            department_id: Optional[int] = None,
                            social_media_link: Optional[str] = None,
                            birthday: Optional[str] = None,
                            about: Optional[str] = None) -> int:
    query = (
        fr"INSERT INTO profile(account_id, tagline, department_id, social_media_link, birthday, about) "
        fr"     VALUES ('{account_id}','{tagline}','{department_id}', '{social_media_link}', '{birthday}', '{about}')"
        fr"   RETURNING id "
    )
    result = await database.fetch_one(query=query)
    return int(result["id"])


async def read_under_account(account_id: int) -> do.Profile:
    query = (
        fr"SELECT id, account_id, is_birthday_private, tagline, department_id, social_media_link, birthday, about"
        fr"  FROM profile"
        fr" WHERE account_id = '{account_id}'"
    )
    result = await database.fetch_all(query=query)
    if not result:
        raise HTTPException(status_code=404)

    return do.Profile(id=result[0]["id"],
                      account_id=result[0]["account_id"],
                      is_birthday_private=result[0]["is_birthday_private"],
                      tagline=result[0]["tagline"],
                      department_id=result[0]["department_id"],
                      social_media_link=result[0]["social_media_link"],
                      birthday=result[0]["birthday"],
                      about=result[0]["about"])


async def edit_privacy(account_id: int, is_birthday_private: bool = None):
    if is_birthday_private is None:
        return
    query = (
        fr"UPDATE profile"
        fr"   SET is_birthday_private = {is_birthday_private}"
        fr" WHERE account_id = {account_id}"
    )
    await database.fetch_one(query=query)

