from fastapi import APIRouter, Response, HTTPException, Depends, Cookie
from backend.models.schemas import RegisterRequest, LoginRequest
from backend.middleware.auth_middleware import get_current_user, get_optional_user
from datamind.auth.auth import (
    register_user, login_user, logout_user,
    request_password_reset, reset_password, register_guest
)
from typing import Optional

router = APIRouter()

@router.post("/register")
async def register(data: RegisterRequest, response: Response):
    result = register_user(
        data.username, data.email,
        data.password, data.confirm_password
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    # Set session cookie
    response.set_cookie(
        key="session_token",
        value=result["session_token"],
        httponly=True,        # JS cannot read — XSS protection
        samesite="lax",
        max_age=86400,        # 24 hours
        secure=False          # True in production with HTTPS
    )
    return {
        "user": {
            "id":       result["user"]["id"],
            "username": result["user"]["username"],
            "email":    result["user"]["email"],
            "is_admin": False,
            "is_guest": False
        }
    }

@router.post("/login")
async def login(data: LoginRequest, response: Response):
    result = login_user(data.email, data.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    response.set_cookie(
        key="session_token",
        value=result["session_token"],
        httponly=True,
        samesite="lax",
        max_age=86400,
        secure=False
    )
    return {"user": result["user"]}

@router.post("/logout")
async def logout(response: Response,
                 session_token: Optional[str] = Cookie(None)):
    if session_token:
        logout_user(session_token)
    response.delete_cookie("session_token")
    return {"success": True}

@router.post("/guest")
async def guest_login(response: Response):
    result = register_guest()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    response.set_cookie(
        key="session_token",
        value=result["session_token"],
        httponly=True,
        samesite="lax",
        max_age=86400,
        secure=False
    )
    return {"user": result["user"]}

@router.get("/me")
async def get_me(user=Depends(get_optional_user)):
    return {"user": user}

@router.post("/reset-request")
async def reset_request(data: dict):
    result = request_password_reset(data.get("email",""))
    return {"success": True,
            "token": result.get("reset_token")}

@router.post("/reset-password")
async def do_reset(data: dict):
    result = reset_password(
        data.get("token",""), data.get("new_password",""))
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"success": True}
