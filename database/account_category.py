from typing import Sequence, Optional

from fastapi import HTTPException

from main import database
from base import do, enum


async def browse_account_categories(account_id: int) -> do.AccountCategory:
    query = (
        fr"SELECT account_id, category_id"
        fr" FROM account_category "
        fr"WHERE account_id = {account_id}"
    )
    result = await database.fetch_all(query=query)
    return [do.AccountCategory(account_id=result[i]["account_id"],
                               category_id=result[i]["category_id"])
            for i in range(len(result))]


