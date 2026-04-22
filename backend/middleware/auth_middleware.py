from fastapi import Depends, HTTPException, Cookie
from typing import Optional
import database as db

async def get_current_user(
    session_token: Optional[str] = Cookie(None)
) -> dict:
    if not session_token:
        raise HTTPException(status_code=401,
                           detail="Not authenticated")
    from datamind.auth.auth import validate_session
    user = validate_session(session_token)
    if not user:
        raise HTTPException(status_code=401,
                           detail="Session expired")
    return user

async def get_optional_user(
    session_token: Optional[str] = Cookie(None)
) -> Optional[dict]:
    # Returns None for guests, user dict for logged-in
    if not session_token:
        return None
    try:
        return await get_current_user(session_token)
    except HTTPException:
        return None
