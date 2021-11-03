from typing import Sequence, Optional, Dict

from fastapi import HTTPException

from main import database
from base import do, enum


async def browse_by_search(to_search: str) -> Sequence[do.Account]:
    search_sql = fr"username LIKE '%{to_search}%' OR real_name LIKE '%{to_search}%'"
    query = (
        fr"SELECT id, username, pass_hash, real_name, email, gender,"
        fr"       is_real_name_private, is_superuser, is_deleted"
        fr"  FROM account"
        fr" WHERE {search_sql}"
        fr"   AND NOT is_deleted"
    )
    result = await database.fetch_all(query=query)
    return [do.Account(id=result[i]["id"],
                       username=result[i]["username"],
                       pass_hash=result[i]["pass_hash"],
                       real_name=result[i]["real_name"],
                       email=result[i]["email"],
                       gender=enum.GenderType(result[i]["gender"]),
                       is_real_name_private=result[i]["is_real_name_private"],
                       is_superuser=result[i]["is_superuser"],
                       is_deleted=result[i]["is_deleted"])
            for i in range(len(result))]


async def read(account_id: int) -> do.Account:
    query = (
        fr"SELECT id, username, pass_hash, real_name, email, gender,"
        fr"       is_real_name_private, is_superuser, is_deleted"
        fr"  FROM account" 
        fr" WHERE id = {account_id}"
        fr"   AND NOT is_deleted"
    )
    result = await database.fetch_all(query=query)
    if not result:
        raise HTTPException(status_code=404)

    return do.Account(id=result[0]["id"],
                      username=result[0]["username"],
                      pass_hash=result[0]["pass_hash"],
                      real_name=result[0]["real_name"],
                      email=result[0]["email"],
                      gender=enum.GenderType(result[0]["gender"]),
                      is_real_name_private=result[0]["is_real_name_private"],
                      is_superuser=result[0]["is_superuser"],
                      is_deleted=result[0]["is_deleted"])


async def read_by_username(username: str) -> do.Account:
    query = (
        fr"SELECT id, username, pass_hash, real_name, email, gender,"
        fr"       is_real_name_private, is_superuser, is_deleted"
        fr"  FROM account" 
        fr" WHERE username = '{username}'"
        fr"   AND NOT is_deleted"
    )
    result = await database.fetch_all(query=query)
    if not result:
        raise HTTPException(status_code=400, detail="Login Failed")

    return do.Account(id=result[0]["id"],
                      username=result[0]["username"],
                      pass_hash=result[0]["pass_hash"],
                      real_name=result[0]["real_name"],
                      email=result[0]["email"],
                      gender=enum.GenderType(result[0]["gender"]),
                      is_real_name_private=result[0]["is_real_name_private"],
                      is_superuser=result[0]["is_superuser"],
                      is_deleted=result[0]["is_deleted"])


async def batch_read(account_ids: Sequence[int]) -> Sequence[do.Account]:
    cond_sql = ', '.join(str(account_id) for account_id in account_ids)
    query = (
        fr"SELECT id, username, pass_hash, real_name, email, gender,"
        fr"       is_real_name_private, is_superuser, is_deleted"
        fr"  FROM account"
        fr" WHERE id IN ({cond_sql})"
        fr"   AND NOT is_deleted"
    )
    result = await database.fetch_all(query=query)
    return [do.Account(id=result[i]["id"],
                       username=result[i]["username"],
                       pass_hash=result[i]["pass_hash"],
                       real_name=result[i]["real_name"],
                       email=result[i]["email"],
                       gender=enum.GenderType(result[i]["gender"]),
                       is_real_name_private=result[i]["is_real_name_private"],
                       is_superuser=result[i]["is_superuser"],
                       is_deleted=result[i]["is_deleted"])
            for i in range(len(result))]


async def add(username: str, pass_hash: str, real_name: str, email: str,
              gender: enum.GenderType, is_superuser: Optional[bool] = False) -> int:
    query = (
        fr"INSERT INTO account(username, pass_hash, real_name, email, gender, is_superuser) "
        fr"     VALUES ('{username}','{pass_hash}','{real_name}', '{email}', '{gender}', '{is_superuser}')"
        fr"   RETURNING id "
    )
    result = await database.fetch_one(query=query)
    return int(result["id"])


async def edit_privacy(account_id: int, is_real_name_private: bool = None):
    if is_real_name_private is None:
        return
    query = (
        fr"UPDATE account"
        fr"   SET is_real_name_private = {is_real_name_private}"
        fr" WHERE id = {account_id}"
    )
    await database.fetch_one(query=query)

