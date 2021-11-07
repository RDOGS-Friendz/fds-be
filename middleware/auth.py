import fastapi
from base import security
from datetime import datetime


async def middleware(request: fastapi.Request, call_next):
    if auth_token := request.headers.get('auth-token', None):
        account_id = security.decode_jwt(auth_token, time=datetime.now())
        request.state.id = account_id
    return await call_next(request)
