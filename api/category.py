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

router = APIRouter(
    tags=['Category'],
)

@router.get("/category/{category_id}", response_model=do.Category)
async def read_category(category_id: int):
    result = await db.category.read_category(category_id=category_id)
    if result:
        return do.Category(id=result['id'], name=result['name'])
    raise HTTPException(status_code=404, detail="Not Found")

@dataclass
class BrowseCategoryOutput:
    id: int
    name: str


@router.get("/category", response_model=Sequence[BrowseCategoryOutput])
async def browse_category(search: str = ''):
    if search != '':
        result = await db.category.search_categories(search=search.lower())
        results = [do.Category(id=item['id'], name=item['name']) for item in result]
        return results
    result = await db.category.read_all_categories()
    results = [do.Category(id=item['id'], name=item['name']) for item in result]
    return results

@dataclass
class BatchCategoryOutput:
    id: int
    name: str

@router.get("/category/batch", response_model=Sequence[BatchCategoryOutput])
async def batch_get_category(category_ids: pydantic.Json, request: Request):
    category_ids = pydantic.parse_obj_as(list[int], category_ids)
    if not category_ids:
        return []
    result = await db.category.batch_read(category_ids=category_ids)
    return [BrowseCategoryOutput(id=category.id,
                                name=category.name)
                        for category in result]