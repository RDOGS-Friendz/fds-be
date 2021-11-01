from typing import Sequence, Optional
from datetime import datetime

from fastapi import HTTPException
from starlette.responses import StreamingResponse

from main import database
from base import do, enum

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