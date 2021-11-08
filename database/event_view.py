from typing import Sequence, Tuple, Dict
from datetime import datetime

from main import database
from base import do, enum
from middleware.response import json_serial
import const


async def view_all(viewer_id: int, filter: Dict[str, str], limit: int, offset: int) \
        -> Tuple[Sequence[do.EventView], int]:

    filter_list = []
    customized_fields = ['start_date', 'end_date', 'title']

    for field_name, value in filter.items():
        if field_name not in customized_fields:
            filter_list.append(fr"{field_name} = '{value}'")

    if 'start_date' in filter:
        filter_list.append(fr" start_time >= '{filter['start_date']}' ")
    if 'end_date' in filter:
        filter_list.append(fr" start_time <= '{filter['end_date']}' ")
    if 'title' in filter:
        filter_list.append(fr" title LIKE '%{filter['title']}%' ")

    filter_sql = ''
    if filter_list:
        filter_sql = ' AND '.join(filter_list)

    query = (
        fr"SELECT * FROM ("
        fr" SELECT *, "
        fr"        id in (SELECT event_id FROM event_bookmark WHERE account_id = {viewer_id}) as is_bookmarked"  # return bookmarked or not
        fr"  FROM view_event "
        fr" WHERE (NOT is_private"
        fr"         OR (is_private AND (creator_account_id = ANY(get_account_friend({viewer_id}))"
        fr"             OR id IN (SELECT event_id FROM event_participant WHERE account_id = {viewer_id})))"
        fr"       )"
        fr" ) AS __TABLE__ "
        fr"{  f' WHERE {filter_sql}' if filter_sql else ''}"
        fr" ORDER BY id DESC"
        fr" LIMIT {limit} OFFSET {offset}"
    )
    results = await database.fetch_all(query=query)

    cnt_query = (
        fr"SELECT COUNT(*) FROM ("
        fr" SELECT * FROM view_event"
        fr"  WHERE (NOT is_private"
        fr"         OR (is_private AND (creator_account_id = ANY(get_account_friend({viewer_id}))"
        fr"             OR id IN (SELECT event_id FROM event_participant WHERE account_id = {viewer_id})))"
        fr"       )"
        fr" ) AS __TABLE__ "
        fr"{  f' WHERE {filter_sql}' if filter_sql else ''}"
    )
    total_count = await database.fetch_one(query=cnt_query)

    return ([do.EventView(id=result["id"],
                          title=result["title"],
                          is_private=result["is_private"],
                          location_id=result["location_id"],
                          category_id=result["category_id"],
                          intensity=enum.IntensityType(result["intensity"]),
                          create_time=json_serial(result["create_time"]),
                          start_time=json_serial(result["start_time"]),
                          end_time=json_serial(result["end_time"]),
                          max_participant_count=result["max_participant_count"],
                          creator_account_id=result["creator_account_id"],
                          description=result["description"],
                          participant_ids=result["participant_id"],
                          bookmarked=result["is_bookmarked"])
            for result in results], int(total_count["count"]))


async def view_suggested(viewer_id: int, filter: Dict[str, str], limit: int, offset: int) \
        -> Tuple[Sequence[do.EventView], int]:
    filter_list = []
    customized_fields = ['start_date', 'end_date']

    for field_name, value in filter.items():
        if field_name not in customized_fields:
            filter_list.append(fr"{field_name} = '{value}'")

    if 'start_date' in filter:
        filter_list.append(fr" start_time >= '{filter['start_date']}' ")
    if 'end_date' in filter:
        filter_list.append(fr" start_time <= '{filter['end_date']}' ")

    filter_sql = ''
    if filter_list:
        filter_sql = ' AND '.join(filter_list)

    query = (
        fr"SELECT * FROM ("
        fr" SELECT *, "
        fr"        id in (SELECT event_id FROM event_bookmark WHERE account_id = {viewer_id}) as is_bookmarked"  # return bookmarked or not
        fr"  FROM view_event"
        fr" WHERE start_time >= NOW()"
        fr"   AND (NOT is_private"
        fr"         OR (is_private AND (creator_account_id = ANY(get_account_friend({viewer_id}))"
        fr"             OR id IN (SELECT event_id FROM event_participant WHERE account_id = {viewer_id})))"
        fr"       )"
        fr"   AND category_id IN ( SELECT category_id FROM account_category WHERE account_id =  {viewer_id})"  # interested categories
        fr"   AND (id NOT IN (SELECT event_id FROM event_participant WHERE account_id =  {viewer_id}))"  # not joined
        fr") AS __TABLE__ "
        fr"{  f' WHERE {filter_sql}' if filter_sql else ''}"
        fr" ORDER BY id DESC"
        fr" LIMIT {limit} OFFSET {offset}"
    )
    results = await database.fetch_all(query=query)

    cnt_query = (
        fr"SELECT COUNT(*) FROM ("
        fr" SELECT * FROM view_event"
        fr" WHERE start_time >= NOW()"
        fr"   AND (NOT is_private"
        fr"         OR (is_private AND (creator_account_id = ANY(get_account_friend({viewer_id}))"
        fr"             OR id IN (SELECT event_id FROM event_participant WHERE account_id = {viewer_id})))"
        fr"       )"
        fr"   AND category_id IN ( SELECT category_id FROM account_category WHERE account_id = {viewer_id})"  # interested categories
        fr"   AND (id NOT IN (SELECT event_id FROM event_participant WHERE account_id = {viewer_id}))"  # not joined
        fr") AS __TABLE__ "
        fr"{  f' WHERE {filter_sql}' if filter_sql else ''}"
    )
    total_count = await database.fetch_one(query=cnt_query)

    return ([do.EventView(id=result["id"],
                          title=result["title"],
                          is_private=result["is_private"],
                          location_id=result["location_id"],
                          category_id=result["category_id"],
                          intensity=enum.IntensityType(result["intensity"]),
                          create_time=json_serial(result["create_time"]),
                          start_time=json_serial(result["start_time"]),
                          end_time=json_serial(result["end_time"]),
                          max_participant_count=result["max_participant_count"],
                          creator_account_id=result["creator_account_id"],
                          description=result["description"],
                          participant_ids=result["participant_id"],
                          bookmarked=result["is_bookmarked"])
             for result in results], int(total_count["count"]))


async def view_upcoming(viewer_id: int, filter: Dict[str, str], limit: int, offset: int) \
        -> Tuple[Sequence[do.EventView], int]:
    filter_list = []
    customized_fields = ['start_date', 'end_date', 'time_interval']

    for field_name, value in filter.items():
        if field_name not in customized_fields:
            filter_list.append(fr"{field_name} = '{value}'")

    if 'start_date' in filter:
        filter_list.append(fr" start_time >= '{filter['start_date']}' ")
    if 'end_date' in filter:
        filter_list.append(fr" start_time <= '{filter['end_date']}' ")
    if 'time_interval' not in filter:
        filter['time_interval'] = const.DEFAULT_TIME_INTERVAL
    filter_list.append(fr" start_time - NOW() <= interval '{filter['time_interval']}'")

    filter_sql = ''
    if filter_list:
        filter_sql = ' AND '.join(filter_list)

    query = (
        fr"SELECT * FROM ("
        fr" SELECT *, "
        fr"        id in (SELECT event_id FROM event_bookmark WHERE account_id = {viewer_id}) as is_bookmarked"  # return bookmarked or not
        fr"  FROM view_event"
        fr" WHERE start_time >= NOW()"
        fr"   AND (NOT is_private"
        fr"         OR (is_private AND (creator_account_id = ANY(get_account_friend({viewer_id}))"
        fr"             OR id IN (SELECT event_id FROM event_participant WHERE account_id = {viewer_id})))"
        fr"       )"
        fr"   AND (id IN (SELECT event_id FROM event_participant WHERE account_id = {viewer_id}))"  # joined
        fr") AS __TABLE__ "
        fr"{  f' WHERE {filter_sql}' if filter_sql else ''}"
        fr" ORDER BY id DESC"
        fr" LIMIT {limit} OFFSET {offset}"
    )
    results = await database.fetch_all(query=query)

    cnt_query = (
        fr"SELECT COUNT(*) FROM ("
        fr" SELECT * FROM view_event"
        fr" WHERE start_time >= NOW()"
        fr"   AND (NOT is_private"
        fr"         OR (is_private AND (creator_account_id = ANY(get_account_friend({viewer_id}))"
        fr"             OR id IN (SELECT event_id FROM event_participant WHERE account_id = {viewer_id})))"
        fr"       )"
        fr"   AND (id IN (SELECT event_id FROM event_participant WHERE account_id = {viewer_id}))"  # joined
        fr") AS __TABLE__ "
        fr"{f' WHERE {filter_sql}' if filter_sql else ''}"
    )
    total_count = await database.fetch_one(query=cnt_query)

    return ([do.EventView(id=result["id"],
                          title=result["title"],
                          is_private=result["is_private"],
                          location_id=result["location_id"],
                          category_id=result["category_id"],
                          intensity=enum.IntensityType(result["intensity"]),
                          create_time=json_serial(result["create_time"]),
                          start_time=json_serial(result["start_time"]),
                          end_time=json_serial(result["end_time"]),
                          max_participant_count=result["max_participant_count"],
                          creator_account_id=result["creator_account_id"],
                          description=result["description"],
                          participant_ids=result["participant_id"],
                          bookmarked=result["is_bookmarked"])
             for result in results], int(total_count["count"]))


async def view_joined_by_friend(viewer_id: int, filter: Dict[str, str], limit: int, offset: int) \
        -> Tuple[Sequence[do.EventView], int]:
    filter_list = []
    customized_fields = ['start_date', 'end_date']

    for field_name, value in filter.items():
        if field_name not in customized_fields:
            filter_list.append(fr"{field_name} = '{value}'")

    if 'start_date' in filter:
        filter_list.append(fr" start_time >= '{filter['start_date']}' ")
    if 'end_date' in filter:
        filter_list.append(fr" start_time <= '{filter['end_date']}' ")

    filter_sql = ''
    if filter_list:
        filter_sql = ' AND '.join(filter_list)

    query = (
        fr"SELECT * FROM ("
        fr" SELECT *, "
        fr"        id in (SELECT event_id FROM event_bookmark WHERE account_id = {viewer_id}) as is_bookmarked"  # return bookmarked or not
        fr"  FROM view_event"
        fr" WHERE id = ANY(event_joined_by_friend({viewer_id}))"  # joined by friend (not include self)
        fr"   AND (NOT is_private"
        fr"         OR (is_private AND (creator_account_id = ANY(get_account_friend({viewer_id}))"
        fr"             OR id IN (SELECT event_id FROM event_participant WHERE account_id = {viewer_id})))"
        fr"   )"
        fr") AS __TABLE__ "
        fr"{ f' WHERE {filter_sql}' if filter_sql else ''}"
        fr" ORDER BY id DESC"
        fr" LIMIT {limit} OFFSET {offset}"
    )
    results = await database.fetch_all(query=query)

    cnt_query = (
        fr"SELECT COUNT(*) FROM ("
        fr" SELECT * FROM view_event"
        fr" WHERE id = ANY(event_joined_by_friend({viewer_id}))"  # joined by friend (not include self)
        fr"   AND (NOT is_private"
        fr"         OR (is_private AND (creator_account_id = ANY(get_account_friend({viewer_id}))"
        fr"             OR id IN (SELECT event_id FROM event_participant WHERE account_id = {viewer_id})))"
        fr"   )"
        fr") AS __TABLE__ "
        fr"{f' WHERE {filter_sql}' if filter_sql else ''}"
    )
    total_count = await database.fetch_one(query=cnt_query)

    return ([do.EventView(id=result["id"],
                          title=result["title"],
                          is_private=result["is_private"],
                          location_id=result["location_id"],
                          category_id=result["category_id"],
                          intensity=enum.IntensityType(result["intensity"]),
                          create_time=json_serial(result["create_time"]),
                          start_time=json_serial(result["start_time"]),
                          end_time=json_serial(result["end_time"]),
                          max_participant_count=result["max_participant_count"],
                          creator_account_id=result["creator_account_id"],
                          description=result["description"],
                          participant_ids=result["participant_id"],
                          bookmarked=result["is_bookmarked"])
             for result in results], int(total_count["count"]))


async def view_bookmarked(viewer_id: int, filter: Dict[str, str], limit: int, offset: int) \
        -> Tuple[Sequence[do.EventView], int]:
    filter_list = []
    customized_fields = ['start_date', 'end_date']

    for field_name, value in filter.items():
        if field_name not in customized_fields:
            filter_list.append(fr"{field_name} = '{value}'")

    if 'start_date' in filter:
        filter_list.append(fr" start_time >= '{filter['start_date']}' ")
    if 'end_date' in filter:
        filter_list.append(fr" start_time <= '{filter['end_date']}' ")

    filter_sql = ''
    if filter_list:
        filter_sql = ' AND '.join(filter_list)

    query = (
        fr"SELECT * FROM ("
        fr" SELECT *, "
        fr"        id in (SELECT event_id FROM event_bookmark WHERE account_id = {viewer_id}) as is_bookmarked"  # return bookmarked or not
        fr"   FROM view_event"
        fr"  WHERE id IN (SELECT event_id FROM event_bookmark WHERE account_id = {viewer_id})"
        fr"    AND (NOT is_private "
        fr"         OR (is_private AND (creator_account_id = ANY(get_account_friend({viewer_id}))"
        fr"             OR id IN (SELECT event_id FROM event_participant WHERE account_id = {viewer_id})))"
        fr"       )"
        fr") AS __TABLE__ "
        fr"{ f' WHERE {filter_sql}' if filter_sql else ''}"
        fr" ORDER BY id DESC"
        fr" LIMIT {limit} OFFSET {offset}"
    )
    results = await database.fetch_all(query=query)

    cnt_query = (
        fr"SELECT COUNT(*) FROM ("
        fr" SELECT * FROM view_event "
        fr"  WHERE id IN (SELECT event_id FROM event_bookmark WHERE account_id = {viewer_id})"
        fr"    AND (NOT is_private "
        fr"         OR (is_private AND (creator_account_id = ANY(get_account_friend({viewer_id}))"
        fr"             OR id IN (SELECT event_id FROM event_participant WHERE account_id = {viewer_id})))"
        fr"       )"
        fr") AS __TABLE__ "
        fr"{f' WHERE {filter_sql}' if filter_sql else ''}"
    )
    total_count = await database.fetch_one(query=cnt_query)

    return ([do.EventView(id=result["id"],
                          title=result["title"],
                          is_private=result["is_private"],
                          location_id=result["location_id"],
                          category_id=result["category_id"],
                          intensity=enum.IntensityType(result["intensity"]),
                          create_time=json_serial(result["create_time"]),
                          start_time=json_serial(result["start_time"]),
                          end_time=json_serial(result["end_time"]),
                          max_participant_count=result["max_participant_count"],
                          creator_account_id=result["creator_account_id"],
                          description=result["description"],
                          participant_ids=result["participant_id"],
                          bookmarked=result["is_bookmarked"])
             for result in results], int(total_count["count"]))
