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

router = APIRouter(
    tags=['Bookmark'],
    dependencies=[Depends(get_token_header)],
)


@dataclass
class AddBookmarkOutput:
    id: int

@router.post("/event/{event_id}/bookmark", response_model=AddBookmarkOutput)
async def add_bookmark(event_id: int, request: Request):
    """
    ### Auth
    - Self
    """
    result = await db.bookmark.add_bookmark(event_id=event_id, account_id=request.state.id)
    if result == None:
        raise HTTPException(status_code=400, detail="System Exception")
    return do.AddOutput(id=int(result['id']))

@router.delete("/event/bookmark/{bookmark_id}")
async def delete_bookmark(bookmark_id: int, request: Request):
    """
    ### Auth
    - Self
    """
    result = await db.bookmark.delete_bookmark(bookmark_id=bookmark_id, account_id=request.state.id)
    if result == None:
        raise HTTPException(status_code=400, detail="No Permission")
    return do.AddOutput(id=bookmark_id)