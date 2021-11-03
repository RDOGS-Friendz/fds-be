from typing import Sequence, Optional
from datetime import datetime

from fastapi import HTTPException
from starlette.responses import StreamingResponse

from main import database
from base import do, enum
from middleware.response import json_serial


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
        fr"SELECT id, title, is_private, location_id, category_id, intensity, "
        fr"       create_time, start_time, end_time, max_participant_count, creator_account_id, description"
        fr" FROM event"
        fr" WHERE id={event_id}"
    )
    result = await database.fetch_one(query=query)
    return do.Event(id=result["id"],
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
                    description=result["description"])

async def join_event(event_id: int, account_id: int):
    query = (
        fr"INSERT INTO event_participant (account_id, event_id) "
        fr"  VALUES ({account_id}, {event_id})"
        fr" ON CONFLICT DO NOTHING"
    )
    await database.fetch_one(query=query)

async def cancel_join_event(event_id: int, account_id: int):
    query = (
        fr"DELETE FROM event_participant"
        fr"  WHERE account_id={account_id} AND event_id={event_id}"
    )
    await database.fetch_one(query=query)


async def get_event_participants_cnt(event_id: int):
    query = (
        fr"SELECT COUNT(*)"
        fr"   FROM event_participant"
        fr" WHERE event_id={event_id}"
    )
    result = await database.fetch_one(query=query)
    return int(result['count'])

async def get_event_max_participants_cnt(event_id: int):
    query = (
        fr"SELECT max_participant_count"
        fr"   FROM event"
        fr" WHERE id={event_id}"
    )
    result = await database.fetch_one(query=query)
    return int(result['max_participant_count'])

async def edit_event(event_id: int, account_id: int, title: str = None, is_private: bool= None, location_id: int= None, 
                     category_id: int= None, intensity: enum.IntensityType= None, start_time: datetime= None, 
                     end_time: datetime= None,  max_participant_count: int= None, description: str= None) -> None:
    to_updates = {}

    if title is not None:
        to_updates['title'] = title
    if is_private is not None:
        to_updates['is_private'] = is_private
    if location_id is not None:
        to_updates['location_id'] = location_id
    if category_id is not None:
        to_updates['category_id'] = category_id
    if intensity is not None:
        to_updates['intensity'] = intensity
    if start_time is not None:
        to_updates['start_time'] = start_time
    if end_time is not None:
        to_updates['end_time'] = end_time
    if max_participant_count is not None:
        to_updates['max_participant_count'] = max_participant_count
    if description is not None:
        to_updates['description'] = description

    if not to_updates:
        return
    
    set_sql = ', '.join(fr"{field_name} = '{to_updates[field_name]}'" for field_name in to_updates)
    
    query = (fr'UPDATE event'
             fr'   SET {set_sql}'
             fr' WHERE creator_account_id = {account_id} AND id={event_id}')
    await database.fetch_one(query=query)

async def delete_event(event_id: int, account_id: int) -> None:
    query = (fr'DELETE FROM event'
             fr' WHERE id = {event_id} AND creator_account_id={account_id}')
    await database.fetch_one(query=query)