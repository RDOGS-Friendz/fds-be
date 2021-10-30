from fastapi import Header, HTTPException, Depends


async def get_token_header(auth_token: str = Header(None, convert_underscores=True)):
    pass
