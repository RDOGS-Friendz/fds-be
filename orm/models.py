from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, Enum, Table
from sqlalchemy.orm import relationship
from .database import Base
from .types import Gender, Intensity, Location_Type, Friendship_Type


EventParticipantRelation = Table(
    "event_participant", Base.metadata,
    Column('account_id', Integer, ForeignKey('account.id')),
    Column('event_id', Integer, ForeignKey('event.id')),
)


EventBookMarkRelation = Table(
    "event_bookmark", Base.metadata,
    Column('account_id', Integer, ForeignKey('account.id')),
    Column('event_id', Integer, ForeignKey('event.id')),
)


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    real_name = Column(String, index=True, nullable=False)
    email = Column(String, index=True, nullable=False)
    gender = Column('gender', Enum(Gender), index=True, nullable=False)

    participant_events = relationship(
        'Event',
        secondary=EventParticipantRelation,
        back_populates="participant_accounts",
    )

    bookmark_events = relationship(
        'Event',
        secondary=EventBookMarkRelation,
    )

    # created_events = relationship("Event", back_populates="created_account")


class Event(Base):
    __tablename__ = "event"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    is_private = Column(Boolean, index=True, nullable=False, default=False)
    location_id = Column(Integer, ForeignKey("location.id"))
    category_id = Column(Integer, ForeignKey("category.id"))
    intensity = Column('intensity', Enum(Intensity), default="INTERMEDIATE")
    create_time = Column(DateTime, nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    max_participant_count = Column(Integer)
    creator_account_id = Column(Integer, ForeignKey("account.id"))
    description = Column(String, nullable=True)

    # location = relationship("Location", back_populates="events")
    # category = relationship("Category", back_populates="events")
    # created_account = relationship("Account", back_populates="created_events")
    participant_accounts = relationship(
        'Account',
        secondary=EventParticipantRelation,
        back_populates="participant_events",
    )


class Location(Base):
    __tablename__ = "location"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    type = Column('location_type', Enum(Location_Type), default="NONE")

    # events = relationship("Event", back_populates="location")


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    
    # events = relationship("Event", back_populates="category")


# class Friendship(Base):
#     __tablename__ = "friendship"
#
#     requester_id = Column(Integer, ForeignKey("account.id"), primary_key=True)
#     addressee_id = Column(Integer, ForeignKey("account.id"), primary_key=True)
#     status = Column('friendship_type', Enum(Friendship_Type), default="PENDING")
#
#     requester_user = relationship("Account", foreign_keys=[requester_id])
#     addressee_user = relationship("Account", foreign_keys=[addressee_id])


# class EventParticipant(Base):
#     __tablename__ = "event_participant"
#     account_id = Column(Integer, ForeignKey("account.id"), primary_key=True)
#     event_id = Column(Integer, ForeignKey("event.id"), primary_key=True)
