from typing import Sequence, Optional

from fastapi import HTTPException

from main import database
from base import do, enum

# async def get_account_friends(account_id: int) -> Sequence[Optional[int]]:
#     query = (
#         fr"SELECT requester_id, addressee_id"
#         fr" FROM friendship"
#         fr" WHERE (requester_id={account_id} AND status='ACCEPTED')"
#         fr"  OR (addressee_id={account_id} AND status='ACCEPTED')"
#     )
#     results = await database.fetch_all(query=query)
#     list1 = []
#     for result in results:
#         list1.append(result['addressee_id'])
#         list1.append(result['requester_id'])
#     return list(filter((account_id).__ne__, list1))

async def read_category(category_id: int):
    query = (
        fr"SELECT id, name"
        fr" FROM category"
        fr" WHERE id={category_id}"
    )
    return await database.fetch_one(query=query)

