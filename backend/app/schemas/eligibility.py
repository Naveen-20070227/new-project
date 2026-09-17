from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ProfileInput(BaseModel):
    name: str
    age: int
    gender: str
    caste: str = "SC"
    area: str
    district: str
    state: str

class BusinessFormInput(BaseModel):
    purpose: str
    unit: str # New or Expanding
    description: Optional[str] = ""

class EducationFormInput(BaseModel):
    course_name: str
    college_name: str
    number_of_years: int

class CheckEligibilityRequest(BaseModel):
    profile: ProfileInput
    annual_income: float = Field(..., gt=0)
    amount_required: float = Field(..., gt=0)
    product_cost: float = Field(..., gt=0) # Product Cost or Total Course Fees
    loan_type: str # Business Loan or Education
    business_form: Optional[BusinessFormInput] = None
    education_form: Optional[EducationFormInput] = None

class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = []

class SchemeEligibilityStatus(BaseModel):
    scheme_code: str
    scheme_name: str
    status: str # ELIGIBLE, NOT_ELIGIBLE, REQUIRES_INFORMATION
    reasons: List[str]
