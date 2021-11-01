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
    tags=['Friend'],
    dependencies=[Depends(get_token_header)],
)

class AddFriendInput(BaseModel):
    friend_account_id: int

class PatchFriendInput(BaseModel):
    friend_request_id: int
    action: str

@router.get("/account/{account_id}/friends")
async def read_account_friends(account_id: int, request: Request):
    """
    ### Auth
    - Self
    """
    if request.state.id is not account_id:
        raise HTTPException(status_code=400, detail="No Permission")
    list = await db.friend.get_account_friends(account_id=account_id)
    return do.FriendOutput(friend_account_id=list)

@router.get("/account/{account_id}/friend-request")
async def read_account_friend_requests(account_id: int, request: Request):
    """
    ### Auth
    - Self
    """
    if request.state.id is not account_id:
        raise HTTPException(status_code=400, detail="No Permission") 
    list = await db.friend.get_friend_requests(account_id=account_id)
    return do.FriendRequestOutput(friend_request_id=list)

@router.post("/account/{account_id}/friend-request")
async def send_friend_request(account_id: int, data: AddFriendInput, request: Request) -> do.AddOutput:
    """
    ### Auth
    - Self
    """
    if request.state.id is not account_id:
        raise HTTPException(status_code=400, detail="No Permission")
    status = await db.friend.send_friend_request(account_id=account_id, friend_id=data.friend_account_id)
    
    if status != 'Successful':
        raise HTTPException(status_code=400, detail="You are already friends")
    return do.AddOutput(id=data.friend_account_id)

@router.patch("/account/{account_id}/friend-request")
async def edit_friend_request(account_id: int, data: PatchFriendInput, request: Request) -> do.AddOutput:
    """
    ### Auth
    - Self
    """
    if request.state.id is not account_id:
        raise HTTPException(status_code=400, detail="No Permission")
    # judge action is accept or decline
    if data.action == 'accept':
        await db.friend.accept_friend_request(account_id=account_id, friend_id=data.friend_request_id)
    elif data.action == 'decline':
        await db.friend.decline_friend_request(account_id=account_id, friend_id=data.friend_request_id)
    else:
        raise HTTPException(status_code=400, detail="System Exception")