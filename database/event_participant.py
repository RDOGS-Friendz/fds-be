from typing import Sequence, Optional

from fastapi import HTTPException

from main import database
from base import do, enum


async def browse_participants(event_id: int) -> Sequence[int]:
    query = (
        fr"SELECT account_id, event_id"
        fr" FROM event_participant "
        fr"WHERE event_id = {event_id} "
    )
    results = await database.fetch_all(query=query)
    return [result["account_id"] for result in results]