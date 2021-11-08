import enum


class Gender(enum.Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    OTHER = 'OTHER'


class Intensity(enum.Enum):
    HIGH = "HIGH"
    INTERMEDIATE = "INTERMEDIATE"
    LOW = "LOW"


class Location_Type(enum.Enum):
    NONE = "NONE"
    INDOOR = "INDOOR"
    OUTDOOR = "OUTDOOR"
    BOTH = "BOTH"


class Friendship_Type(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DELETED = "DELETED"


class AccountEventViewType(str, enum.Enum):
    ALL = 'ALL'
    HISTORY = 'HISTORY'
    UPCOMING = 'UPCOMING'
