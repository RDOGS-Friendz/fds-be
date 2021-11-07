from enum import Enum


class GenderType(str, Enum):
    male = 'MALE'
    female = 'FEMALE'
    other = 'OTHER'


class GenderType(str, Enum):
    male = 'MALE'
    female = 'FEMALE'
    other = 'OTHER'

class IntensityType(str, Enum):
    high = 'HIGH'
    intermediate = 'INTERMEDIATE'
    low = 'LOW'

class LocationType(str, Enum):
    none = 'NONE'
    indoor = 'INDOOR'
    outdoor = 'OUTDOOR'
    both = 'BOTH'

class FriendshipType(str, Enum):
    pending = 'PENDING'
    accepted = 'ACCEPTED'
    deleted = 'DELETED'

class EventViewType(str, Enum):
    all = 'all'
    suggested = 'suggested'
    upcoming = 'upcoming'
    joined_by_friend = 'joined-by-friend'
    bookmarked = 'bookmarked'
