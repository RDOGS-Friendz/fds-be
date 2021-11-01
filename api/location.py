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
    tags=['Location'],
    dependencies=[Depends(get_token_header)],
)

class AddLocationInput(BaseModel):
    name: str
    type: enum.LocationType

class SearchLocationInput(BaseModel):
    search: Optional[str] = None

@router.post("/location")
async def add_location(data: AddLocationInput, request: Request) -> do.AddOutput:
    location_id = await db.location.add_location(name=data.name, type=data.type)
    return do.AddOutput(id=location_id)

@router.get("/location/{location_id}")
async def read_location(location_id: int):
    result = await db.location.read_location(location_id=location_id)
    if result:
        return do.Location(id=result['id'], name=result['name'], type=result['type'], lat=result['lat'], lng=result['lng'])
    raise HTTPException(status_code=404, detail="Not Found")

# TODO: ADD search option
@router.get("/location")
async def browse_all_location(search: str = ''):
    if search != '':
        result = await db.location.search_locations(search=search)
        results = [do.Location(id=item['id'], name=item['name'], type=item['type'], lat=item['lat'], lng=item['lng']) for item in result]
        return do.LocationsOutput(locations=results)
    result = await db.location.read_all_locations()
    results = [do.Location(id=item['id'], name=item['name'], type=item['type'], lat=item['lat'], lng=item['lng']) for item in result]
    return do.LocationsOutput(locations=results)