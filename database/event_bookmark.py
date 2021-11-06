from typing import Sequence, Tuple

from main import database
from base import do, enum
from middleware.response import json_serial


async def browse_bookmarked_events(account_id: int, limit: int, offset: int) \
        -> Tuple[Sequence[Tuple[do.Event, Sequence[int]]], int]:
    query = (
        fr"SELECT * FROM view_event "
        fr" WHERE id IN (SELECT event_id FROM event_bookmark WHERE account_id = {account_id})"
        fr"   AND (NOT is_private "
        fr"         OR (is_private AND (creator_account_id = ANY(get_account_friend({account_id}))"
        fr"             OR id IN (SELECT event_id FROM event_participant WHERE account_id = {account_id})))"
        fr"       )"
        fr" ORDER BY id DESC"
        fr" LIMIT {limit} OFFSET {offset}"
    )
    results = await database.fetch_all(query=query)

    cnt_query = (
        fr"SELECT COUNT(*) FROM view_event "
        fr" WHERE id IN (SELECT event_id FROM event_bookmark WHERE account_id = {account_id})"
        fr"   AND (NOT is_private "
        fr"         OR (is_private AND (creator_account_id = ANY(get_account_friend({account_id}))"
        fr"             OR id IN (SELECT event_id FROM event_participant WHERE account_id = {account_id})))"
        fr"       )"
    )
    total_count = await database.fetch_one(query=cnt_query)

    return ([(do.Event(id=result["id"],
                       title=result["title"],
                       is_private=result["is_private"],
                       location_id=result["location_id"],
                       category_id=result["category_id"],
                       intensity=enum.IntensityType(result["intensity"]),
                       create_time=json_serial(result["create_time"]),
                       start_time=json_serial(result["start_time"]),
                       end_time=json_serial(result["end_time"]),
                       max_participant_count=result["max_participant_count"],
                       creator_account_id=result["creator_account_id"],
                       description=result["description"]
                       ),
              result["participant_id"])
             for result in results], int(total_count["count"]))
