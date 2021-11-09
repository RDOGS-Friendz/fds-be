from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from . import crud, models, schema, types
from .database import SessionLocal, engine
from middleware.dependencies import get_token_header
from typing import List

router = APIRouter(
    tags=['Event'],
    dependencies=[Depends(get_token_header)],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/account/{account_id}/event", response_model=schema.Account_Event_with_Count)
async def browse_event_by_account(
        account_id: int,
        db: Session = Depends(get_db),
        view: types.AccountEventViewType = types.AccountEventViewType.ALL,
        limit: int = 50,
        offset: int = 0,
):
    """
        ### Auth
        No Auth
    """
    events, total_count = crud.browse_event_by_account(
        db=db,
        account_id=account_id,
        view=view,
        limit=limit,
        offset=offset
    )
    return schema.Account_Event_with_Count(
        data=[schema.Event(
            id=event.id,
            title=event.title,
            is_private=event.is_private,
            location_id=event.location_id,
            category_id=event.category_id,
            intensity=event.intensity,
            create_time=event.create_time,
            start_time=event.start_time,
            end_time=event.end_time,
            max_participant_count=event.max_participant_count,
            creator_account_id=event.creator_account_id,
            participant_accounts=[participant.id for participant in event.participant_accounts],
        ) for event in events],
        total_event_count=total_count,
    )
