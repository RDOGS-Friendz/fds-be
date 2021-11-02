from typing import Sequence, Optional

from fastapi import HTTPException

from main import database
from base import do, enum


async def browse_bookmarked_events(account_id: int) -> Sequence[do.EventBookmark]:
    query = (
        fr"SELECT id, account_id, event_id"
        fr" FROM event_bookmark "
        fr"WHERE account_id = {account_id} "
    )
    result = await database.fetch_all(query=query)
    return [do.EventBookmark(id=result[i]["id"],
                             account_id=result[i]["account_id"],
                             event_id=result[i]["event_id"])
            for i in range(len(result))]