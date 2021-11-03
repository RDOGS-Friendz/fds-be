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
    tags=['Reaction'],
    dependencies=[Depends(get_token_header)],
)

class AddReactionInput(BaseModel):
    content: str

class EditReactionInput(BaseModel):
    content: str

@router.post("/event/{event_id}/reaction")
async def add_reaction(event_id: int, data: AddReactionInput, request: Request) -> do.AddOutput:
    """
    ### Auth
    - Self
    """
    result = await db.reaction.add_event_reaction(event_id=event_id, account_id=request.state.id, content=data.content)
    if result == None:
        raise HTTPException(status_code=400, detail="System Exception")
    return do.AddOutput(id=int(result['id']))

@router.get("/event/{event_id}/reaction")
async def browse_event_reactions(event_id: int):
    result = await db.reaction.read_event_reactions(event_id=event_id)
    results = [do.Reaction(id=item['id'], event_id=item['event_id'], content=item['content'], author_id=item['author_id']) for item in result]
    return do.ReactionsOutput(reactions=results)

@router.patch("/event/{event_id}/reaction")
async def edit_event_reaction(event_id: int, data: EditReactionInput, request: Request) -> None:
    """
    ### Auth
    - Self
    """
    try:
        await db.reaction.edit_reaction(event_id=event_id, account_id=request.state.id, content=data.content)
    except:
        raise HTTPException(status_code=400, detail="System Exception")

@router.delete("/event/{event_id}/reaction")
async def delete_event_reaction(event_id: int, request: Request):
    """
    ### Auth
    - Self
    """
    result = await db.reaction.delete_reaction(event_id=event_id, account_id=request.state.id)
    if result == None:
        raise HTTPException(status_code=400, detail="No Permission")
    return do.AddOutput(id=int(result['id']))