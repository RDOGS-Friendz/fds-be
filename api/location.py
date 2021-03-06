from typing import Sequence, Optional
from datetime import datetime
import pydantic

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
    lat: Optional[float]
    lng: Optional[float]

class SearchLocationInput(BaseModel):
    search: Optional[str] = None

@dataclass
class BatchLocationOutput:
    id: int
    name: str
    type: enum.LocationType
    lat: Optional[float]
    lng: Optional[float]

@router.get("/location/batch", response_model=Sequence[BatchLocationOutput])
async def batch_get_location(location_ids: pydantic.Json, request: Request):
    location_ids = pydantic.parse_obj_as(list[int], location_ids)
    if not location_ids:
        return []
    result = await db.location.batch_read(location_ids=location_ids)
    return [BrowseLocationOutput(id=location.id,
                                name=location.name,
                                type=location.type,
                                lat=location.lat,
                                lng=location.lng)
                        for location in result]

@dataclass
class AddLocationOutput:
    id: int


@router.post("/location", response_model=AddLocationOutput)
async def add_location(data: AddLocationInput, request: Request) -> do.AddOutput:
    location_id = await db.location.add_location(name=data.name, type=data.type, lat=data.lat, lng=data.lng)
    return do.AddOutput(id=location_id)


@router.get("/location/{location_id}", response_model=do.Location)
async def read_location(location_id: int) -> do.Location:
    result = await db.location.read_location(location_id=location_id)
    if result:
        return do.Location(id=result['id'], name=result['name'], type=result['type'], lat=result['lat'], lng=result['lng'])
    raise HTTPException(status_code=404, detail="Not Found")


@dataclass
class BrowseLocationOutput:
    id: int
    name: str
    type: enum.LocationType
    lat: Optional[float]
    lng: Optional[float]


@router.get("/location", response_model=Sequence[BrowseLocationOutput])
async def browse_location(search: str = ''):
    if search != '':
        result = await db.location.search_locations(search=search)
        results = [do.Location(id=item['id'], name=item['name'], type=item['type'], lat=item['lat'], lng=item['lng']) for item in result]
        return results
    result = await db.location.read_all_locations()
    results = [do.Location(id=item['id'], name=item['name'], type=item['type'], lat=item['lat'], lng=item['lng']) for item in result]
    return results

