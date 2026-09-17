from pydantic import BaseModel, Field
from typing import Optional

class OTPRequest(BaseModel):
    mobile_number: str = Field(..., description="10-digit mobile number")

class OTPResponse(BaseModel):
    message: str
    mobile_number: str
    cooldown_seconds: int
    dev_otp: Optional[str] = None # Available in development mode

class RegisterRequest(BaseModel):
    beneficiary_name: str
    mobile_number: str
    otp: str

class LoginRequest(BaseModel):
    mobile_number: str
    otp: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    beneficiary_name: str
    mobile_number: str
    profile_complete: bool
