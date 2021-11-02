from typing import Sequence, Optional

from fastapi import HTTPException

from main import database
from base import do, enum

async def read_bookmarks(account_id: int, limit: int, offset: int):
    query = (
        fr"SELECT id, event_id, account_id"
        fr" FROM event_bookmark"
        fr" WHERE account_id={account_id}"
        fr"  ORDER BY id DESC"
        fr"  LIMIT {limit} OFFSET {offset}"
    )
    return await database.fetch_one(query=query)

async def add_bookmark(event_id: int, account_id: int):
    query = (
        fr"INSERT INTO event_bookmark(event_id, account_id) "
        fr"  VALUES ({event_id}, {account_id})"
        fr" ON CONFLICT DO NOTHING"
        fr" RETURNING id"
    )
    result = await database.fetch_one(query=query)
    return result

async def delete_bookmark(bookmark_id: int, account_id: int):
    query = (
        fr"DELETE FROM event_bookmark"
        fr" WHERE id={bookmark_id} AND account_id={account_id}"
        fr" RETURNING id"
    )
    return await database.fetch_one(query=query)

