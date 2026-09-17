import random
import re
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.app.core.config import settings
from backend.app.models.user import OTPRecord

def validate_mobile_number(mobile: str) -> str:
    cleaned = re.sub(r"\D", "", mobile)
    if len(cleaned) == 12 and cleaned.startswith("91"):
        cleaned = cleaned[2:]
    if len(cleaned) != 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid mobile number format. Please provide a 10-digit Indian mobile number."
        )
    return cleaned

def generate_otp(db: Session, mobile_number: str) -> dict:
    mobile = validate_mobile_number(mobile_number)
    now = datetime.now(timezone.utc)
    
    # Check rate limiting / cooldown
    last_otp = db.query(OTPRecord).filter(
        OTPRecord.mobile_number == mobile
    ).order_by(OTPRecord.created_at.desc()).first()
    
    if last_otp:
        time_since_last = (now - last_otp.created_at.replace(tzinfo=timezone.utc)).total_seconds()
        if time_since_last < settings.OTP_COOLDOWN_SECONDS:
            remaining = int(settings.OTP_COOLDOWN_SECONDS - time_since_last)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Please wait {remaining} seconds before requesting another OTP."
            )
    
    # Generate 6-digit OTP code
    otp_code = str(random.randint(100000, 999999))
    expires_at = now + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    resend_allowed_at = now + timedelta(seconds=settings.OTP_COOLDOWN_SECONDS)
    
    new_record = OTPRecord(
        mobile_number=mobile,
        otp_code=otp_code,
        expires_at=expires_at,
        resend_allowed_at=resend_allowed_at,
        attempts=0,
        is_used=False
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    
    response = {
        "message": f"OTP successfully sent to {mobile}",
        "mobile_number": mobile,
        "cooldown_seconds": settings.OTP_COOLDOWN_SECONDS
    }
    
    if settings.OTP_DEV_MODE:
        response["dev_otp"] = otp_code
        
    return response

def verify_otp(db: Session, mobile_number: str, input_otp: str) -> bool:
    mobile = validate_mobile_number(mobile_number)
    now = datetime.now(timezone.utc)
    
    record = db.query(OTPRecord).filter(
        OTPRecord.mobile_number == mobile,
        OTPRecord.is_used == False
    ).order_by(OTPRecord.created_at.desc()).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active OTP request found for this mobile number. Please request a new OTP."
        )
    
    # Expiry check
    exp_time = record.expires_at.replace(tzinfo=timezone.utc) if record.expires_at.tzinfo is None else record.expires_at
    if now > exp_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new OTP."
        )
    
    # Max attempts check
    if record.attempts >= settings.OTP_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum OTP verification attempts exceeded. Please request a new OTP."
        )
    
    if record.otp_code != input_otp.strip():
        record.attempts += 1
        db.commit()
        remaining_attempts = settings.OTP_MAX_ATTEMPTS - record.attempts
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OTP. {remaining_attempts} attempt(s) remaining."
        )
    
    # Mark OTP as used
    record.is_used = True
    db.commit()
    return True
