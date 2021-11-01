from typing import Sequence, Optional

from fastapi import HTTPException

from main import database
from base import do, enum

async def read_location(location_id: int):
    query = (
        fr"SELECT id, name, type, lat, lng"
        fr" FROM location"
        fr" WHERE id={location_id}"
    )
    return await database.fetch_one(query=query)

async def read_all_locations():
    query = (
        fr"SELECT id, name, type, lat, lng"
        fr" FROM location"
    )
    return await database.fetch_all(query=query)

async def add_location(name: str, type: enum.LocationType):
    query = (
        fr"INSERT INTO location(name, type) "
        fr"  VALUES ('{name}', '{type}')"
        fr" RETURNING id"
    )
    result = await database.fetch_one(query=query)
    return int(result["id"])
