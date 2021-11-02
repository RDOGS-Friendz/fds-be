from typing import Sequence, Optional

from fastapi import HTTPException

from main import database
from base import do, enum


async def read(department_id: int) -> do.Department:
    query = (
        fr"SELECT id, school, department_name"
        fr" FROM department "
        fr"WHERE id = {department_id}"
    )
    result = await database.fetch_all(query=query)
    return do.Department(id=result[0]["id"],
                         school=result[0]["school"],
                         department_name=result[0]["department_name"])