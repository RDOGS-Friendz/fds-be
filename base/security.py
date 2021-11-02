from datetime import datetime, timedelta
from functools import partial
from fastapi import HTTPException

import jwt
from passlib.hash import argon2
import hashlib

from config import jwt_config


_jwt_encoder = partial(jwt.encode, key=jwt_config.jwt_secret, algorithm=jwt_config.jwt_encode_algorithm)
_jwt_decoder = partial(jwt.decode, key=jwt_config.jwt_secret, algorithms=[jwt_config.jwt_encode_algorithm])


def encode_jwt(account_id: int) -> str:
    return _jwt_encoder({
        'account-id': account_id
    })


def decode_jwt(encoded: str) -> int:
    try:
        decoded = _jwt_decoder(encoded)
    except jwt.DecodeError:  # FIXME: catch failed
        raise HTTPException(status_code=400, detail="Login Failed")

    return decoded['account-id']


def hash_password(password: str) -> str:
    return argon2.hash(password)


def verify_password(to_test: str, hashed: str) -> bool:
    return argon2.verify(to_test, hashed)
