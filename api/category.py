from typing import Sequence, Optional
from datetime import datetime

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

@router.get("/category/{category_id}")
async def read_category(category_id: int):
    result = await db.category.read_category(category_id=category_id)
    if result:
        return do.Category(id=result['id'], name=result['name'])
    raise HTTPException(status_code=404, detail="Not Found")
