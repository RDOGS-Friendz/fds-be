from datetime import datetime
from typing import Sequence, Optional

from fastapi import HTTPException

from main import database
from base import do, enum
from middleware.response import json_serial
from . import department


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
                      birthday=json_serial(result[0]["birthday"]),
                      about=result[0]["about"])


async def edit_under_account(account_id: int, tagline: str = None, department_name: str = None,
                             social_media_link: str = None, birthday: datetime = None,
                             preferred_category_ids: Sequence[int] = None, about: str = None) -> None:
    to_updates = {}

    if tagline is not None:
        to_updates['tagline'] = tagline
    if department_name is not None:
        department_id = await department.read_by_name(department_name=department_name)
        to_updates['department_id'] = department_id
    if social_media_link is not None:
        to_updates['social_media_link'] = social_media_link
    if birthday is not None:
        to_updates['birthday'] = birthday
    if about is not None:
        to_updates['about'] = about

    if not to_updates:
        return

    set_sql = ', '.join(fr"{field_name} = '{to_updates[field_name]}'" for field_name in to_updates)

    query = (fr'UPDATE profile'
             fr'   SET {set_sql}'
             fr' WHERE account_id = {account_id}')
    await database.fetch_one(query=query)

    if preferred_category_ids is not None:
        # Delete
        query = (fr'DELETE FROM account_category'
                 fr' WHERE account_id = {account_id}')
        await database.fetch_one(query=query)

        # Add
        add_sql = '), ('.join(fr"{account_id}, {category_id}" for category_id in preferred_category_ids)
        query = (fr'INSERT INTO account_category '
                 fr'VALUES ({add_sql})')
        await database.fetch_one(query=query)


async def edit_privacy(account_id: int, is_birthday_private: bool = None):
    if is_birthday_private is None:
        return
    query = (
        fr"UPDATE profile"
        fr"   SET is_birthday_private = {is_birthday_private}"
        fr" WHERE account_id = {account_id}"
    )
    await database.fetch_one(query=query)

