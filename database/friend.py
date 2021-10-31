from typing import Sequence, Optional

from fastapi import HTTPException

from main import database
from base import do, enum

async def get_account_friends(account_id: int) -> Sequence[Optional[str]]:
    query = (
        fr"SELECT requester_id, addressee_id"
        fr" FROM friendship"
        fr" WHERE (requester_id={account_id} OR addressee_id={account_id})"
        fr" AND status='ACCEPTED'"
    )
    results = await database.fetch_all(query=query)
    results = [ item for result in results for item in result]
    return list(filter((account_id).__ne__, results))

async def get_friend_requests(account_id: int) -> Sequence[Optional[str]]:
    query = (
        fr"SELECT requester_id"
        fr" FROM friendship"
        fr" WHERE addressee_id={account_id} AND status='PENDING'"
    )
    results = await database.fetch_all(query=query)
    results = [ item for result in results for item in result]
    return list(filter((account_id).__ne__, results))

async def send_friend_request(account_id: int, friend_id: int) -> str:
    # check whether they have been friends or not
    query = (
        fr"SELECT requester_id, addressee_id"
        fr"  FROM friendship"
        fr" WHERE (requester_id={account_id} AND addressee_id={friend_id} AND status='ACCEPTED')"
        fr"  OR (requester_id={friend_id} AND addressee_id={account_id} AND status='ACCEPTED')"    
    )
    results = await database.fetch_all(query=query)
    if len(results) > 0:
        return 'You are friends'
    # if not insert or update
    query = (
        fr"INSERT INTO friendship (requester_id, addressee_id, status)"
        fr" VALUES ({account_id}, {friend_id}, 'PENDING')"
        fr" ON CONFLICT (requester_id, addressee_id) DO"
        fr" UPDATE SET status = 'PENDING';"
    )
    await database.fetch_one(query=query)

    return 'Successful'


