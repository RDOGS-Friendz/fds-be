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

async def search_locations(search: str):
    query = (
        fr"SELECT id, name, type, lat, lng"
        fr" FROM location"
        fr" WHERE name LIKE '%{search}%'"
    )
    return await database.fetch_all(query=query)

async def add_location(name: str, type: enum.LocationType, lat: float, lng: float) -> int:
    query = (
        fr"INSERT INTO location(name, type, lat, lng) "
        fr"  VALUES ('{name}', '{type}', '{lat}', '{lng}')"
        fr" RETURNING id"
    )
    result = await database.fetch_one(query=query)
    return int(result["id"])


async def batch_read(location_ids: Sequence[int]) -> Sequence[do.Location]:
    cond_sql = ', '.join(str(location_id) for location_id in location_ids)
    query = (
        fr"SELECT id, name, type, lat, lng"
        fr"  FROM location"
        fr" WHERE id IN ({cond_sql})"
    )
    result = await database.fetch_all(query=query)
    return [do.Location(id=result[i]["id"],
                       name=result[i]["name"],
                       type=enum.LocationType(result[i]["type"]),
                       lat=result[i]["lat"],
                       lng=result[i]["lng"])
            for i in range(len(result))]