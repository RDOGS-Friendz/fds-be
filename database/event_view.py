from typing import Sequence, Tuple, Dict
from datetime import datetime

from main import database
from base import do, enum
from middleware.response import json_serial
import const


async def view_all(viewer_id: int, filter: Dict[str, str], limit: int, offset: int) \
        -> Sequence[Tuple[do.Event, Sequence[int]]]:

    filter_sql = ''

    if filter:
        if 'start_date' in filter and 'end_date' in filter:
            filter_sql = ' AND '.join(fr" start_date BETWEEN DATE '{filter['start_date']}' and DATE '{filter['end_date']}' ")
        if filter_sql:
            filter_sql += ' AND '
        filter_sql += ' AND '.join(fr"{field_name} = '{value}'" for field_name, value in filter.items()
                                   if field_name not in ['start_date', 'end_date'])

    query = (
        fr"SELECT * FROM (SELECT * FROM "
		fr" (SELECT *, "
		fr"		CASE WHEN (end_time - start_time) < INTERVAL '30 minutes' then 'SHORT'"
		fr"		     WHEN (end_time - start_time) < INTERVAL '90 minutes' then 'MEDIUM'"
		fr"		     ELSE 'LONG'"
		fr"		 END duration , "
		fr"		CASE WHEN EXTRACT(HOUR FROM start_time) BETWEEN 5 AND 12 THEN 'MORNING'"
		fr"			 WHEN EXTRACT(HOUR FROM start_time) BETWEEN 12 AND 18 THEN 'AFTERNOON'"
		fr"			 WHEN EXTRACT(HOUR FROM start_time) BETWEEN 18 AND 23 THEN 'EVENING'"
		fr"			 ELSE 'NIGHT'"
		fr"		 END day_time,"
        fr"     (SELECT DISTINCT ARRAY_AGG(ep.account_id) FROM event e"
		fr"		   LEFT JOIN event_participant ep "
		fr"				  ON ep.event_id = e.id"
		fr"			   WHERE ep.account_id is not null "
		fr"			     AND event.id = ep.event_id) AS participant_ids,"
		fr"      start_time::TIMESTAMP::DATE AS start_date"
        fr"   FROM event) as t "
        fr"   WHERE start_time >= NOW()"
        fr" AND (is_private AND ( "  # private
        fr"     creator_account_id IN ( "  # is_friend
        fr"     SELECT * FROM (" 
        fr"           SELECT DISTINCT UNNEST(ARRAY[requester_id, addressee_id]) AS friend_id FROM friendship"
        fr"            WHERE (status='ACCEPTED') AND (requester_id = {viewer_id} OR addressee_id = {viewer_id})) AS t)"
        fr"     ) " 
        fr" ) "
        fr" OR NOT is_private"
        fr" OR ( id IN"  # is joined
        fr"       (SELECT event_id FROM event_participant WHERE account_id = {viewer_id}))"
        fr" ) AS __TABLE__ "
        fr"{  f' WHERE {filter_sql}' if filter_sql else ''}"
        fr" ORDER BY id DESC"
        fr" LIMIT {limit} OFFSET {offset}"
    )
    results = await database.fetch_all(query=query)
    return [(do.Event(id=result["id"],
                      title=result["title"],
                      is_private=result["is_private"],
                      location_id=result["location_id"],
                      category_id=result["category_id"],
                      intensity=enum.IntensityType(result["intensity"]),
                      create_time=json_serial(["create_time"]),
                      start_time=json_serial(result["start_time"]),
                      end_time=json_serial(result["end_time"]),
                      max_participant_count=result["max_participant_count"],
                      creator_account_id=result["creator_account_id"],
                      description=result["description"]
                     ),
             result["participant_ids"])
            for result in results]


async def view_suggested(viewer_id: int, filter: Dict[str, str], limit: int, offset: int) \
        -> Sequence[Tuple[do.Event, Sequence[int]]]:

    filter_sql = ''

    if filter:
        if 'start_date' in filter and 'end_date' in filter:
            filter_sql = ' AND '.join(fr" start_date BETWEEN DATE '{filter['start_date']}' and DATE '{filter['end_date']}' ")
        if filter_sql:
            filter_sql += ' AND '
        filter_sql += ' AND '.join(fr"{field_name} = '{value}'" for field_name, value in filter.items()
                                  if field_name not in ['start_date', 'end_date'])

    query = (
        fr"SELECT * FROM (SELECT * FROM "
		fr" (SELECT *, "
		fr"		CASE WHEN (end_time - start_time) < INTERVAL '30 minutes' then 'SHORT'"
		fr"		     WHEN (end_time - start_time) < INTERVAL '90 minutes' then 'MEDIUM'"
		fr"		     ELSE 'LONG'"
		fr"		 END duration , "
		fr"		CASE WHEN EXTRACT(HOUR FROM start_time) BETWEEN 5 AND 12 THEN 'MORNING'"
		fr"			 WHEN EXTRACT(HOUR FROM start_time) BETWEEN 12 AND 18 THEN 'AFTERNOON'"
		fr"			 WHEN EXTRACT(HOUR FROM start_time) BETWEEN 18 AND 23 THEN 'EVENING'"
		fr"			 ELSE 'NIGHT'"
		fr"		 END day_time,"
        fr"     (SELECT DISTINCT ARRAY_AGG(ep.account_id) FROM event e"
		fr"		   LEFT JOIN event_participant ep "
		fr"				  ON ep.event_id = e.id"
		fr"			   WHERE ep.account_id is not null "
		fr"			     AND event.id = ep.event_id) AS participant_ids,"
		fr"      start_time::TIMESTAMP::DATE AS start_date" 
        fr"   FROM event) as t "
        fr"   WHERE start_time >= NOW()"
        fr" AND category_id IN ( "  # interested categories
	    fr"     SELECT category_id FROM account_category"
	    fr"      WHERE account_id = {viewer_id}) "
        fr" AND ((is_private AND ( "  # private
        fr"     creator_account_id IN ( "  # is_friend
        fr"     SELECT * FROM (" 
        fr"           SELECT DISTINCT UNNEST(ARRAY[requester_id, addressee_id]) AS friend_id FROM friendship"
        fr"            WHERE (status='ACCEPTED') AND (requester_id = {viewer_id} OR addressee_id = {viewer_id})) AS t)"
        fr"     ) " 
        fr" ) OR NOT is_private)"
        fr" AND ( id NOT IN"  # is not joined
        fr"       (SELECT event_id FROM event_participant WHERE account_id = {viewer_id}))"
        fr" ) AS __TABLE__"
        fr"{  f' WHERE {filter_sql}' if filter_sql else ''}"
        fr" ORDER BY id DESC"
        fr" LIMIT {limit} OFFSET {offset}"
    )
    results = await database.fetch_all(query=query)
    return [(do.Event(id=result["id"],
                      title=result["title"],
                      is_private=result["is_private"],
                      location_id=result["location_id"],
                      category_id=result["category_id"],
                      intensity=enum.IntensityType(result["intensity"]),
                      create_time=json_serial(["create_time"]),
                      start_time=json_serial(result["start_time"]),
                      end_time=json_serial(result["end_time"]),
                      max_participant_count=result["max_participant_count"],
                      creator_account_id=result["creator_account_id"],
                      description=result["description"]
                     ),
             result["participant_ids"])
            for result in results]


async def view_upcoming(viewer_id: int, filter: Dict[str, str], limit: int, offset: int) \
        -> Sequence[Tuple[do.Event, Sequence[int]]]:

    if 'time_interval' not in filter:
        filter['time_interval'] = const.DEFAULT_TIME_INTERVAL
    filter_sql = fr" start_time - NOW() <= interval '{filter['time_interval']}'"

    if 'start_date' in filter and 'end_date' in filter:
        filter_sql += ' AND '
        filter_sql += ' AND '.join(fr" start_date BETWEEN DATE '{filter['start_date']}' and DATE '{filter['end_date']}' ")

    to_add_sql = ' AND '.join(fr"{field_name} = '{value}'" for field_name, value in filter.items()
                              if field_name not in ['start_date', 'end_date', 'time_interval'])
    if to_add_sql:
        filter_sql += ' AND '
        filter_sql += to_add_sql



    query = (
        fr"SELECT * FROM (SELECT * FROM "
		fr" (SELECT *, "
		fr"		CASE WHEN (end_time - start_time) < INTERVAL '30 minutes' then 'SHORT'"
		fr"		     WHEN (end_time - start_time) < INTERVAL '90 minutes' then 'MEDIUM'"
		fr"		     ELSE 'LONG'"
		fr"		 END duration , "
		fr"		CASE WHEN EXTRACT(HOUR FROM start_time) BETWEEN 5 AND 12 THEN 'MORNING'"
		fr"			 WHEN EXTRACT(HOUR FROM start_time) BETWEEN 12 AND 18 THEN 'AFTERNOON'"
		fr"			 WHEN EXTRACT(HOUR FROM start_time) BETWEEN 18 AND 23 THEN 'EVENING'"
		fr"			 ELSE 'NIGHT'"
		fr"		 END day_time,"
        fr"     (SELECT DISTINCT ARRAY_AGG(ep.account_id) FROM event e"
		fr"		   LEFT JOIN event_participant ep "
		fr"				  ON ep.event_id = e.id"
		fr"			   WHERE ep.account_id is not null "
		fr"			     AND event.id = ep.event_id) AS participant_ids,"
		fr"      start_time::TIMESTAMP::DATE AS start_date" 
        fr"   FROM event) as t "
        fr" WHERE start_time >= NOW()"
        fr" AND (is_private AND ( "  # private
        fr"     creator_account_id IN ( "  # is_friend
        fr"     SELECT * FROM (" 
        fr"           SELECT DISTINCT UNNEST(ARRAY[requester_id, addressee_id]) AS friend_id FROM friendship"
        fr"            WHERE (status='ACCEPTED') AND (requester_id = {viewer_id} OR addressee_id = {viewer_id})) AS t)"
        fr"     ) " 
        fr" ) "
        fr" OR NOT is_private"
        fr" OR ( id IN"  # is joined
        fr"      (SELECT event_id FROM event_participant WHERE account_id = {viewer_id}))"
        fr" ) AS __TABLE__"
        fr"{  f' WHERE {filter_sql}' if filter_sql else ''}"
        fr" ORDER BY id DESC"
        fr" LIMIT {limit} OFFSET {offset}"
    )
    results = await database.fetch_all(query=query)
    return [(do.Event(id=result["id"],
                      title=result["title"],
                      is_private=result["is_private"],
                      location_id=result["location_id"],
                      category_id=result["category_id"],
                      intensity=enum.IntensityType(result["intensity"]),
                      create_time=json_serial(["create_time"]),
                      start_time=json_serial(result["start_time"]),
                      end_time=json_serial(result["end_time"]),
                      max_participant_count=result["max_participant_count"],
                      creator_account_id=result["creator_account_id"],
                      description=result["description"]
                     ),
             result["participant_ids"])
            for result in results]


async def view_joined_by_friend(viewer_id: int, filter: Dict[str, str], limit: int, offset: int) \
        -> Sequence[Tuple[do.Event, Sequence[int]]]:

    filter_sql = ''

    if filter:
        if 'start_date' in filter and 'end_date' in filter:
            filter_sql = ' AND '.join(fr" start_date BETWEEN DATE '{filter['start_date']}' and DATE '{filter['end_date']}' ")
        if filter_sql:
            filter_sql += ' AND '
        filter_sql += ' AND '.join(fr"{field_name} = '{value}'" for field_name, value in filter.items()
                                   if field_name not in ['start_date', 'end_date'])

    query = (
        fr"SELECT * FROM (SELECT * FROM "
		fr" (SELECT *, "
		fr"		CASE WHEN (end_time - start_time) < INTERVAL '30 minutes' then 'SHORT'"
		fr"		     WHEN (end_time - start_time) < INTERVAL '90 minutes' then 'MEDIUM'"
		fr"		     ELSE 'LONG'"
		fr"		 END duration , "
		fr"		CASE WHEN EXTRACT(HOUR FROM start_time) BETWEEN 5 AND 12 THEN 'MORNING'"
		fr"			 WHEN EXTRACT(HOUR FROM start_time) BETWEEN 12 AND 18 THEN 'AFTERNOON'"
		fr"			 WHEN EXTRACT(HOUR FROM start_time) BETWEEN 18 AND 23 THEN 'EVENING'"
		fr"			 ELSE 'NIGHT'"
		fr"		 END day_time,"
        fr"     (SELECT DISTINCT ARRAY_AGG(ep.account_id) FROM event e"
		fr"		   LEFT JOIN event_participant ep "
		fr"				  ON ep.event_id = e.id"
		fr"			   WHERE ep.account_id is not null "
		fr"			     AND event.id = ep.event_id) AS participant_ids,"
		fr"      start_time::TIMESTAMP::DATE AS start_date"
        fr"   FROM event) as t "
        fr"   WHERE start_time >= NOW()"
        fr"     AND ((is_private AND ( "  # private
        fr"     creator_account_id IN ( "  # is_friend
        fr"     SELECT * FROM (" 
        fr"           SELECT DISTINCT UNNEST(ARRAY[requester_id, addressee_id]) AS friend_id FROM friendship"
        fr"            WHERE (status='ACCEPTED') AND (requester_id = {viewer_id} OR addressee_id = {viewer_id})) AS t)"
        fr"     ) " 
        fr" ) OR NOT is_private)"
        fr" OR ( id IN"  # is joined
        fr"       (SELECT event_id FROM event_participant WHERE account_id = {viewer_id}))"
        fr" AND id IN ( "  # joined by friends
	    fr"    SELECT event_id FROM event_participant "
		fr"     WHERE account_id IN ( "
		fr"           SELECT DISTINCT UNNEST(ARRAY[requester_id, addressee_id]) AS friend_id"
		fr"	     FROM friendship"
		fr"     WHERE (status='ACCEPTED')"
		fr"      AND (requester_id = {viewer_id} or addressee_id = {viewer_id})"
		fr"	    )"
        fr") ) AS __TABLE__ "
        fr"{  f'WHERE {filter_sql}' if filter_sql else ''}"
        fr" ORDER BY id DESC"
        fr" LIMIT {limit} OFFSET {offset}"
    )
    results = await database.fetch_all(query=query)
    return [(do.Event(id=result["id"],
                      title=result["title"],
                      is_private=result["is_private"],
                      location_id=result["location_id"],
                      category_id=result["category_id"],
                      intensity=enum.IntensityType(result["intensity"]),
                      create_time=json_serial(["create_time"]),
                      start_time=json_serial(result["start_time"]),
                      end_time=json_serial(result["end_time"]),
                      max_participant_count=result["max_participant_count"],
                      creator_account_id=result["creator_account_id"],
                      description=result["description"]
                     ),
             result["participant_ids"])
            for result in results]
