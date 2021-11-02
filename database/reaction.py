from typing import Sequence, Optional

from fastapi import HTTPException

from main import database
from base import do, enum

async def read_event_reactions(event_id: int):
    query = (
        fr"SELECT id, event_id, content, author_id"
        fr" FROM event_account_reaction"
        fr" WHERE event_id={event_id}"
    )
    return await database.fetch_all(query=query)

async def add_event_reaction(event_id: int, account_id: int, content: str):
    query = (
        fr"INSERT INTO event_account_reaction(event_id, content, author_id) "
        fr"  VALUES ({event_id}, '{content}', {account_id})"
        fr" ON CONFLICT DO NOTHING"
        fr" RETURNING id"
    )
    result = await database.fetch_one(query=query)
    return int(result["id"])

async def delete_reaction(reaction_id: int, account_id: int):
    query = (
        fr"DELETE FROM event_account_reaction"
        fr" WHERE id={reaction_id} AND author_id={account_id}"
        fr" RETURNING id"
    )
    return await database.fetch_one(query=query)

