import pydantic
import json
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
from middleware.response import SuccessResponse

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


@dataclass
class EventOutput:
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
    description: Optional[str]
    participant_ids: Sequence[int]
    bookmarked: bool


@dataclass
class BrowseEventOutput:
    data: Sequence[EventOutput]
    total_count: int


@router.get("/event", response_model=BrowseEventOutput)
async def browse_event(request: Request, view: enum.EventViewType, search: Optional[pydantic.Json] = '',
                       limit: int = 50, offset: int = 0):
    """
    ### Search String Example:
    ```
    [["is_private", "false"], ["duration", "SHORT"]]
    ```
    ### **Available Search Fields**:
    - is_private: bool
    - category_id: int
    - intensity: `LOW`, `INTERMEDIATE`, `HIGH`
    - duration:
        - `SHORT` (< 30 mins)
        - `MEDIUM` (30 - 90 mins)
        - `LONG` (> 90 mins)
    - day_time:
        - `MORNING` (5-12)
        - `AFTERNOON` (12-18)
        - `EVENING` (18-23)
        - `NIGHT` (23-5)
    - start_date: datetime
    - end_date: datetime
    - creator_account_id: int
    - time_interval **(upcoming event only)** : str (postgres time interval) (default: `1 week`)
    - title **(all only)** : str (support LIKE)
    """
    results = []
    filter_dict = dict()

    if search != '':
        filter_list = pydantic.parse_obj_as(list[list[str]], search)
        for i, filter_ in enumerate(filter_list):
            filter_dict[filter_[0]] = filter_[1]

    if view is enum.EventViewType.suggested:
        results, total_count = await db.event_view.view_suggested(viewer_id=request.state.id, filter=filter_dict, limit=limit, offset=offset)
    elif view is enum.EventViewType.upcoming:
        results, total_count = await db.event_view.view_upcoming(viewer_id=request.state.id, filter=filter_dict, limit=limit, offset=offset)
    elif view is enum.EventViewType.joined_by_friend:
        results, total_count = await db.event_view.view_joined_by_friend(viewer_id=request.state.id, filter=filter_dict, limit=limit, offset=offset)
    elif view is enum.EventViewType.bookmarked:
        results, total_count = await db.event_view.view_bookmarked(viewer_id=request.state.id, filter=filter_dict, limit=limit, offset=offset)
    else:  # all
        results, total_count = await db.event_view.view_all(viewer_id=request.state.id, filter=filter_dict, limit=limit, offset=offset)

    return BrowseEventOutput(
        data=[EventOutput(
                id=event.id, title=event.title, is_private=event.is_private, location_id=event.location_id,
                category_id=event.category_id, intensity=event.intensity, create_time=event.create_time,
                start_time=event.start_time, end_time=event.end_time, max_participant_count=event.max_participant_count,
                creator_account_id=event.creator_account_id, description=event.description,
                participant_ids=event.participant_ids if event.participant_ids else [],
                bookmarked=event.bookmarked)
            for event in results],
        total_count=total_count)


@router.patch("/event/{event_id}")
async def edit_event(event_id: int, data: EditEventInput, request: Request):
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
        return SuccessResponse()
    except:
        raise HTTPException(status_code=400, detail="System Exception")

@router.delete("/event/{event_id}")
async def delete_event(event_id: int, request: Request):
    """
    ### Auth
    - Creator
    """
    try:
        await db.event.delete_event(event_id=event_id, account_id=request.state.id)
        return SuccessResponse()
    except:
        raise HTTPException(status_code=400, detail="System Exception")


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
    description: Optional[str]
    participant_ids: Sequence[int]
    bookmarked: bool


@router.get("/event/{event_id}", response_model=ReadEventOutput)
async def read_event(event_id: int, request: Request) -> do.Event:
    """
    ### Auth
    - Self
    - Event Participant (Joined Event)
    - Friend of Event Creator
    """
    try:
        event = await db.event.read_event(event_id=event_id, viewer_id=request.state.id)
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

    return ReadEventOutput(id=event.id, title=event.title, is_private=event.is_private, location_id=event.location_id,
                           category_id=event.category_id, intensity=event.intensity, create_time=event.create_time,
                           start_time=event.start_time, end_time=event.end_time, max_participant_count=event.max_participant_count,
                           creator_account_id=event.creator_account_id, description=event.description,
                           participant_ids=event.participant_ids if event.participant_ids else [],
                           bookmarked=event.bookmarked)


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
            return SuccessResponse()
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
        return SuccessResponse()
    except:
        raise HTTPException(status_code=400, detail="System Exception")