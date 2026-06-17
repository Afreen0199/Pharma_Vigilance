from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["User Authentication"])

class AuthRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
def register(request: AuthRequest):
    success = auth_service.register_user(request.email, request.password)
    if not success:
        raise HTTPException(status_code=400, detail="Registration failed. Email may already be registered.")
    return {"message": "User registered successfully.", "status": "success"}

@router.post("/login")
def login(request: AuthRequest):
    token = auth_service.login_user(request.email, request.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {
        "access_token": token,
        "token_type": "bearer",
        "email": request.email
    }
