from typing import Sequence, Optional

from fastapi import HTTPException

from main import database
from base import do, enum

async def get_account_friends(account_id: int) -> Sequence[Optional[int]]:
    query = (
        fr"SELECT requester_id, addressee_id"
        fr" FROM friendship"
        fr" WHERE (requester_id={account_id} AND status='ACCEPTED')"
        fr"  OR (addressee_id={account_id} AND status='ACCEPTED')"
    )
    results = await database.fetch_all(query=query)
    list1 = []
    for result in results:
        list1.append(result['addressee_id'])
        list1.append(result['requester_id'])
    return list(filter((account_id).__ne__, list1))

async def get_friend_requests(account_id: int) -> Sequence[Optional[int]]:
    query = (
        fr"SELECT requester_id"
        fr" FROM friendship"
        fr" WHERE addressee_id={account_id} AND status='PENDING'"
    )
    results = await database.fetch_all(query=query)
    results = [ result["requester_id"] for result in results]
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

async def accept_friend_request(account_id: int, friend_id: int):
    query = (
        fr"UPDATE friendship"
        fr"  SET status='ACCEPTED'"
        fr" WHERE requester_id={friend_id} AND addressee_id={account_id}"
    )
    return await database.fetch_one(query=query)

async def decline_friend_request(account_id: int, friend_id: int):
    query = (
        fr"DELETE FROM friendship"
        fr" WHERE requester_id={friend_id} AND addressee_id={account_id}"
    )
    return await database.fetch_one(query=query)

async def delete_friend(account_id: int, friend_id: int):
    query = (
        fr"DELETE FROM friendship"
        fr" WHERE (requester_id={friend_id} AND addressee_id={account_id})"
        fr" OR (requester_id={account_id} AND addressee_id={friend_id})"
    )
    return await database.fetch_one(query=query)
