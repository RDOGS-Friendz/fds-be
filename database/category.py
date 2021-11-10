from typing import Sequence, Optional

from fastapi import HTTPException

from main import database
from base import do, enum

async def read_category(category_id: int):
    query = (
        fr"SELECT id, name"
        fr" FROM category"
        fr" WHERE id={category_id}"
    )
    return await database.fetch_one(query=query)

async def read_all_categories():
    query = (
        fr"SELECT id, name"
        fr" FROM category"
    )
    return await database.fetch_all(query=query)

async def search_categories(search: str):
    query = (
        fr"SELECT id, name"
        fr" FROM category"
        fr" WHERE Lower(name) LIKE '%{search}%'"
    )
    return await database.fetch_all(query=query)


async def batch_read(category_ids: Sequence[int]) -> Sequence[do.Category]:
    cond_sql = ', '.join(str(category_id) for category_id in category_ids)
    query = (
        fr"SELECT id, name"
        fr"  FROM category"
        fr" WHERE id IN ({cond_sql})"
    )
    result = await database.fetch_all(query=query)
    return [do.Location(id=result[i]["id"],
                       name=result[i]["name"])
            for i in range(len(result))]