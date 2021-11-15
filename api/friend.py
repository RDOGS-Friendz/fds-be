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
from middleware.response import SuccessResponse


router = APIRouter(
    tags=['Friend'],
    dependencies=[Depends(get_token_header)],
)

class AddFriendInput(BaseModel):
    friend_account_id: int

class PatchFriendInput(BaseModel):
    friend_request_id: int
    action: str

@router.get("/account/{account_id}/friends", response_model=do.FriendOutput)
async def read_account_friends(account_id: int, request: Request):
    """
    ### Auth
    - Self
    """
    if request.state.id is not account_id:
        raise HTTPException(status_code=400, detail="No Permission")
    list = await db.friend.get_account_friends(account_id=account_id)
    return do.FriendOutput(friend_account_id=list)

@router.get("/account/{account_id}/friend-request", response_model=do.FriendRequestOutput)
async def read_account_friend_requests(account_id: int, request: Request):
    """
    ### Auth
    - Self
    """
    if request.state.id is not account_id:
        raise HTTPException(status_code=400, detail="No Permission") 
    list = await db.friend.get_friend_requests(account_id=account_id)
    return do.FriendRequestOutput(friend_request_id=list)


@dataclass
class AddFriendOutput:
    id: int


@router.post("/account/{account_id}/friend-request", response_model=AddFriendOutput)
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
async def edit_friend_request(account_id: int, data: PatchFriendInput, request: Request):
    """
    ### Auth
    - Self
    """
    if request.state.id is not account_id:
        raise HTTPException(status_code=400, detail="No Permission")
    # judge action is accept or decline
    if data.action == 'accept':
        try:    
            await db.friend.accept_friend_request(account_id=account_id, friend_id=data.friend_request_id)
            return SuccessResponse()
        except:
            raise HTTPException(status_code=400, detail="System Exception")
    elif data.action == 'decline':
        try:   
            await db.friend.decline_friend_request(account_id=account_id, friend_id=data.friend_request_id)
            return SuccessResponse()
        except:
            raise HTTPException(status_code=400, detail="System Exception")
    else:
        raise HTTPException(status_code=400, detail="System Exception")

class UnfriendInput(BaseModel):
    friend_id: int

@router.delete("/account/{account_id}")
async def delete_friend(account_id: int, data: UnfriendInput, request: Request):
    """
    ### Auth
    - Self
    """
    if request.state.id is not account_id:
        raise HTTPException(status_code=400, detail="No Permission")
    try:
        await db.friend.delete_friend(account_id=account_id, friend_id=data.friend_id)
        return SuccessResponse()
    except:
        raise HTTPException(status_code=400, detail="System Exception")
