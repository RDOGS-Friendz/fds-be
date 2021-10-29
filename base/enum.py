from enum import Enum


class GenderType(str, Enum):
    male = 'MALE'
    female = 'FEMALE'
    other = 'OTHER'
