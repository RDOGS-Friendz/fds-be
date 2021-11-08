import fastapi
from fastapi.responses import JSONResponse
from base import security
from datetime import datetime


async def middleware(request: fastapi.Request, call_next):
    if auth_token := request.headers.get('auth-token', None):  # FIXME: no token should return no permission
        account_data = security.decode_jwt(auth_token, time=datetime.now())
        if isinstance(account_data, int):
            request.state.id = account_data
        else:
            return account_data  # JSONResponse(status_code=401, content={"detail": "No Permission"})
    return await call_next(request)
