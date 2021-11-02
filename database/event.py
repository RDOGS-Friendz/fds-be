from typing import Sequence, Optional
from datetime import datetime

from fastapi import HTTPException
from starlette.responses import StreamingResponse

from main import database
from base import do, enum
from middleware.response import json_serial


# WIP view
async def browse(limit: int, offset: int) -> Sequence[do.Event]:
    query = (
        fr"SELECT id, title, is_private, location_id, category_id, intensity, create_time, "
        fr"       start_time, end_time, max_participant_count, creator_account_id, description"
        fr"  FROM event"
        fr" ORDER BY id DESC"
        fr" LIMIT {limit} OFFSET {offset}"
    )
    result = await database.fetch_all(query=query)
    return [do.Event(id=result[i]["id"],
                     title=result[i]["title"],
                     is_private=result[i]["is_private"],
                     location_id=result[i]["location_id"],
                     category_id=result[i]["category_id"],
                     intensity=enum.IntensityType(result[i]["intensity"]),
                     create_time=result[i]["create_time"],
                     start_time=result[i]["start_time"],
                     end_time=result[i]["end_time"],
                     max_participant_count=result[i]["max_participant_count"],
                     creator_account_id=result[i]["creator_account_id"],
                     description=result[i]["description"]
                     )
            for i in range(len(result))]


async def batch_read(event_ids: Sequence[int], limit: int, offset: int) -> Sequence[do.Event]:

    cond_sql = ', '.join(str(event_id) for event_id in event_ids)
    query = (
        fr"SELECT id, title, is_private, location_id, category_id, intensity, create_time, "
        fr"       start_time, end_time, max_participant_count, creator_account_id, description"
        fr"  FROM event"
        fr'{fr" WHERE id IN ({cond_sql})" if cond_sql else ""}'
        fr" ORDER BY id DESC"
        fr" LIMIT {limit} OFFSET {offset}"
    )
    result = await database.fetch_all(query=query)
    return [do.Event(id=result[i]["id"],
                     title=result[i]["title"],
                     is_private=result[i]["is_private"],
                     location_id=result[i]["location_id"],
                     category_id=result[i]["category_id"],
                     intensity=enum.IntensityType(result[i]["intensity"]),
                     create_time=json_serial(result[i]["create_time"]),
                     start_time=json_serial(result[i]["start_time"]),
                     end_time=json_serial(result[i]["end_time"]),
                     max_participant_count=result[i]["max_participant_count"],
                     creator_account_id=result[i]["creator_account_id"],
                     description=result[i]["description"]
                     )
            for i in range(len(result))]


async def add_event(title: str, is_private: bool, location_id: int, category_id: int, intensity: enum.IntensityType, start_time: datetime,
        end_time: datetime, max_participant_count: int, creator_account_id: int, description: str):
    query = (
        fr"INSERT INTO event (title, is_private, location_id, category_id, intensity, start_time, end_time, max_participant_count, creator_account_id, description) "
        fr"  VALUES ('{title}', {is_private}, {location_id}, {category_id}, '{intensity}', '{start_time}', '{end_time}', {max_participant_count}, {creator_account_id}, '{description}')"
        fr" RETURNING id"
    )
    result = await database.fetch_one(query=query)
    return int(result["id"])

async def read_event(event_id: int):
    query = (
        fr"SELECT id, title, is_private, location_id, category_id, intensity, create_time, start_time, end_time, max_participant_count, creator_account_id, description"
        fr" FROM event"
        fr" WHERE id={event_id}"
    )
    return await database.fetch_one(query=query)

async def join_event(event_id: int, account_id: int):
    query = (
        fr"INSERT INTO event_participant (account_id, event_id) "
        fr"  VALUES ({account_id}, {event_id})"
        fr" ON CONFLICT DO NOTHING"
    )
    await database.fetch_one(query=query)
