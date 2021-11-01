from typing import Sequence, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from databases import Database
from dataclasses import dataclass
from pydantic import BaseModel

from base import do, enum
import database as db
from middleware.dependencies import get_token_header
from middleware.response import json_serial

router = APIRouter(
    tags=['Event'],
    dependencies=[Depends(get_token_header)],
)

class AddEventInput(BaseModel):
    title: str
    is_private: bool
    location_id: int
    category_id: int
    intensity: enum.IntensityType
    start_time: datetime
    end_time: datetime
    num_people_wanted: int
    description: str

@router.post("/event")
async def add_event(data: AddEventInput, request: Request) -> do.AddOutput:
    event_id = await db.event.add_event(title=data.title, is_private=data.is_private, location_id=data.location_id,
     category_id=data.category_id, intensity=data.intensity, start_time=data.start_time, end_time=data.end_time, max_participant_count=data.num_people_wanted, creator_account_id=request.state.id, description=data.description)
    return do.AddOutput(id=event_id)

# TODO: deal with private event
@router.get("/event/{event_id}")
async def read_event(event_id: int):
    result = await db.event.read_event(event_id=event_id)
    if result:
        return do.Event(id=result['id'], title=result['title'], is_private=result['is_private'], location_id=result['location_id'],
             category_id=result['category_id'], intensity=result['intensity'], create_time=json_serial(result['create_time']), start_time=json_serial(result['start_time']),
             end_time=json_serial(result['end_time']), max_participant_count=result['max_participant_count'], creator_account_id=result['creator_account_id'], description=result['description'])
    raise HTTPException(status_code=404, detail="Not Found")
