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


@router.get("/account/{account_id}/event", response_model=List[schema.Event])
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
    return crud.browse_event_by_account(db=db, account_id=account_id, view=view, limit=limit, offset=offset)
