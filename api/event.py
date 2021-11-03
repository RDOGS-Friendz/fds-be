from typing import Sequence, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from databases import Database
from dataclasses import dataclass
from pydantic import BaseModel

from base import do, enum
import database as db
from database import event
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
    try:
        event_id = await db.event.add_event(title=data.title, is_private=data.is_private, location_id=data.location_id,
        category_id=data.category_id, intensity=data.intensity, start_time=data.start_time, end_time=data.end_time, max_participant_count=data.num_people_wanted, creator_account_id=request.state.id, description=data.description)
        await db.event.join_event(event_id=event_id, account_id=request.state.id)
        return do.AddOutput(id=event_id)
    except:
        raise HTTPException(status_code=400, detail="System Exception")

class EditEventInput(BaseModel):
    title: str = None
    is_private: bool = None
    location_id: int = None
    category_id: int = None
    intensity: enum.IntensityType = None
    start_time: datetime = None
    end_time: datetime = None
    num_people_wanted: int = None
    description: str = None

@router.patch("/event/{event_id}")
async def edit_event(event_id: int, data: EditEventInput, request: Request) -> None:
    """
    ### Auth
    - Creator
    """
    try: 
        await db.event.edit_event(event_id=event_id,
                                  account_id=request.state.id,
                                  title=data.title,
                                  is_private=data.is_private,
                                  location_id=data.location_id,
                                  category_id=data.category_id,
                                  intensity=data.intensity,
                                  start_time=data.start_time,
                                  end_time=data.end_time,
                                  max_participant_count=data.num_people_wanted,
                                  description=data.description)
    except:
        raise HTTPException(status_code=400, detail="System Exception")

@router.delete("/event/{event_id}")
async def delete_event(event_id: int, request: Request) -> None:
    """
    ### Auth
    - Creator
    """
    try:
        await db.event.delete_event(event_id=event_id, account_id=request.state.id)
    except:
        raise HTTPException(status_code=400, detail="System Exception")

# filter -> view -> limit, offset
@router.get("/event")
async def browse_event(request: Request, filter: str, view: enum.EventViewType,
                       limit: int = 50, offset: int = 0) -> Sequence[do.Event]:
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


# TODO: exceptions
# TODO: no permission for other users?
@router.get("/event/bookmarked", tags=['Bookmark'], response_model=Sequence[do.Event])
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
    create_time: str
    start_time: str
    end_time: str
    max_participant_count: int
    creator_account_id: int
    description: str


# TODO: deal with private event
@router.get("/event/{event_id}", response_model=ReadEventOutput)
async def read_event(event_id: int, request: Request) -> do.Event:
    """
    ### Auth
    - Self
    - Event Participant (Joined Event)
    - Friend of Event Creator
    """
    try:
        event = await db.event.read_event(event_id=event_id)
    except:
        raise HTTPException(status_code=404, detail="Not Found")

    is_private = event.is_private
    is_self = request.state.id is event.creator_account_id

    participant_ids = await db.event_participant.browse_participants(event_id=event_id)
    is_joined = request.state.id in participant_ids

    friend_ids = await db.friend.get_account_friends(account_id=event.creator_account_id)
    is_friend = request.state.id in friend_ids

    if is_private and (not is_self and not is_joined and not is_friend):
        raise HTTPException(status_code=400, detail="No Permission")

    return event


@router.post("/event/{event_id}/join")
async def join_event(event_id: int, request: Request):
    """
    ### Auth
    - Self
    """
    cur_participants_cnt = await db.event.get_event_participants_cnt(event_id=event_id)
    max_participants_cnt = await db.event.get_event_max_participants_cnt(event_id=event_id)

    if cur_participants_cnt < max_participants_cnt:
        try:
            await db.event.join_event(event_id=event_id, account_id=request.state.id)
        except:
            raise HTTPException(status_code=400, detail="System Exception")
    else:
        raise HTTPException(status_code=400, detail="Max Limitation")

@router.delete("/event/{event_id}/join")
async def cancel_join_event(event_id: int, request: Request) -> None:
    """
    ### Auth
    - Creator
    """
    try:
        await db.event.cancel_join_event(event_id=event_id, account_id=request.state.id)
    except:
        raise HTTPException(status_code=400, detail="System Exception")