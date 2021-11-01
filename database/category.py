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