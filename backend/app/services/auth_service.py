from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.app.models.user import User
from backend.app.models.profile import UserProfile
from backend.app.services.otp_service import verify_otp, validate_mobile_number
from backend.app.core.security import create_access_token
from backend.app.schemas.auth import TokenResponse

def register_user(db: Session, beneficiary_name: str, mobile_number: str, otp: str) -> TokenResponse:
    mobile = validate_mobile_number(mobile_number)
    
    existing_user = db.query(User).filter(User.mobile_number == mobile).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this mobile number already exists. Please proceed to Login."
        )
    
    # Verify OTP
    verify_otp(db, mobile, otp)
    
    new_user = User(
        beneficiary_name=beneficiary_name.strip(),
        mobile_number=mobile,
        is_verified=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    token = create_access_token(new_user.id)
    
    # Auto-create initial profile so beneficiary profile is never empty
    default_profile = UserProfile(
        user_id=new_user.id,
        name=new_user.beneficiary_name,
        age=28,
        gender="Male",
        caste="SC",
        area="Rural",
        district="District Office",
        state="State Office"
    )
    db.add(default_profile)
    db.commit()
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=new_user.id,
        beneficiary_name=new_user.beneficiary_name,
        mobile_number=new_user.mobile_number,
        profile_complete=True
    )

def login_user(db: Session, mobile_number: str, otp: str) -> TokenResponse:
    mobile = validate_mobile_number(mobile_number)
    
    user = db.query(User).filter(User.mobile_number == mobile).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No beneficiary account found for this mobile number. Please register first."
        )
    
    # Verify OTP
    verify_otp(db, mobile, otp)
    
    token = create_access_token(user.id)
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    profile_complete = profile is not None
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        beneficiary_name=user.beneficiary_name,
        mobile_number=user.mobile_number,
        profile_complete=profile_complete
    )
