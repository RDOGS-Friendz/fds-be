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


@dataclass
class AddEventOutput:
    id: int


@router.post("/event", response_model=AddEventOutput)
async def add_event(data: AddEventInput, request: Request) -> do.AddOutput:
    event_id = await db.event.add_event(title=data.title, is_private=data.is_private, location_id=data.location_id,
     category_id=data.category_id, intensity=data.intensity, start_time=data.start_time, end_time=data.end_time, max_participant_count=data.num_people_wanted, creator_account_id=request.state.id, description=data.description)
    await db.event.join_event(event_id=event_id, account_id=request.state.id)
    return do.AddOutput(id=event_id)


# TODO: exceptions
# TODO: no permission for other users?
@router.get("/event/bookmarked", tags=['Bookmark'], response_model=do.Event)
async def browse_bookmarked_event(request: Request, limit: int = 50, offset: int = 0) -> Sequence[do.Event]:
    """
    ### Auth
    - Self
    """
    # if request.state.id is not account_id:
    #     raise HTTPException(status_code=400, detail="No Permission")

    event_bookmarks = await db.event_bookmark.browse_bookmarked_events(account_id=request.state.id)
    events = await db.event.batch_read(event_ids=[bookmark.event_id for bookmark in event_bookmarks],
                                       limit=limit, offset=offset)

    return events


@dataclass
class ReadEventOutput:
    id: int
    title: str
    is_private: bool
    location_id: int
    category_id: int
    intensity: enum.IntensityType
    create_time: datetime
    start_time: datetime
    end_time: datetime
    max_participant_count: int
    creator_account_id: int
    description: str


# TODO: deal with private event
@router.get("/event/{event_id}", response_model=ReadEventOutput)
async def read_event(event_id: int, request: Request) -> do.Event:
    """
    ### Auth
    - Self
    """
    try:
        event = await db.event.read_event(event_id=event_id)
    except:
        raise HTTPException(status_code=404, detail="Not Found")

    is_private = event.is_private
    is_self = request.state.id is event.creator_account_id

    if is_private and not is_self:
        raise HTTPException(status_code=400, detail="No Permission")

    return event


