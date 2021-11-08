from datetime import datetime, timedelta
from functools import partial
from fastapi import HTTPException
from fastapi.responses import JSONResponse

import jwt
from passlib.hash import argon2
import hashlib

from config import jwt_config


_jwt_encoder = partial(jwt.encode, key=jwt_config.jwt_secret, algorithm=jwt_config.jwt_encode_algorithm)
_jwt_decoder = partial(jwt.decode, key=jwt_config.jwt_secret, algorithms=[jwt_config.jwt_encode_algorithm])


def encode_jwt(account_id: int, expire: timedelta) -> str:
    return _jwt_encoder({
        'account-id': account_id,
        'expire': (datetime.now() + expire).isoformat(),
    })


def decode_jwt(encoded: str, time: datetime) -> int:
    try:
        decoded = _jwt_decoder(encoded)
    except jwt.DecodeError:
        return JSONResponse(status_code=401, content={"detail": "Login Failed"})

    expire = datetime.fromisoformat(decoded['expire'])
    if time >= expire:
        return JSONResponse(status_code=401, content={"detail": "Login Expired"})
    return decoded['account-id']


def hash_password(password: str) -> str:
    return argon2.hash(password)


def verify_password(to_test: str, hashed: str) -> bool:
    return argon2.verify(to_test, hashed)
