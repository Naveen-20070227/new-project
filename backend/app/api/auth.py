from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.schemas.auth import (
    OTPRequest, OTPResponse, RegisterRequest, LoginRequest, TokenResponse
)
from backend.app.services.otp_service import generate_otp
from backend.app.services.auth_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/request-otp", response_model=OTPResponse)
def request_otp_endpoint(req: OTPRequest, db: Session = Depends(get_db)):
    """Request a 6-digit OTP sent to the mobile number (Mobile + OTP Auth)."""
    return generate_otp(db, req.mobile_number)

@router.post("/register", response_model=TokenResponse)
def register_endpoint(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new SC beneficiary after OTP verification."""
    return register_user(db, req.beneficiary_name, req.mobile_number, req.otp)

@router.post("/login", response_model=TokenResponse)
def login_endpoint(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate an existing beneficiary via Mobile + OTP."""
    return login_user(db, req.mobile_number, req.otp)

@router.post("/logout")
def logout_endpoint(current_user=Depends(get_current_user)):
    """Logout endpoint invalidating token on client side."""
    return {"message": "Successfully logged out beneficiary session.", "user_id": current_user.id}
