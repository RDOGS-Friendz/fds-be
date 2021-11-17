from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from .import models, schema, types


def browse_event_by_account(db: Session, account_id: int, view: types.AccountEventViewType, limit: int, offset: int, requester_id: int):
    if view == types.AccountEventViewType.all:
        queryset = db.query(models.Event).order_by(models.Event.start_time).filter(
            models.Event.participant_accounts.any(models.Account.id == account_id)
        ).limit(limit).offset(limit*offset).all()
        total_count = db.query(models.Event).order_by(models.Event.start_time).filter(
            models.Event.participant_accounts.any(models.Account.id == account_id)
        ).count()
    if view == types.AccountEventViewType.history:
        queryset = db.query(models.Event).order_by(models.Event.start_time).filter(and_(
            models.Event.participant_accounts.any(models.Account.id == account_id),
            models.Event.start_time <= datetime.now()
        )).limit(limit).offset(limit*offset).all()
        total_count = db.query(models.Event).order_by(models.Event.start_time).filter(and_(
            models.Event.participant_accounts.any(models.Account.id == account_id),
            models.Event.start_time <= datetime.now()
        )).count()
    if view == types.AccountEventViewType.upcoming:
        queryset = db.query(models.Event).order_by(models.Event.start_time).filter(and_(
            models.Event.participant_accounts.any(models.Account.id == account_id),
            models.Event.start_time > datetime.now()
        )).limit(limit).offset(limit * offset).all()
        total_count = db.query(models.Event).order_by(models.Event.start_time).filter(and_(
            models.Event.participant_accounts.any(models.Account.id == account_id),
            models.Event.start_time > datetime.now()
        )).count()

    requester = db.query(models.Account).filter(models.Account.id == requester_id).one()
    return queryset, total_count, requester.bookmark_events

