import math
from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict

router = APIRouter(prefix="/emi", tags=["EMI Calculator"])

class EMICalculationRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Loan amount required in INR")
    rate: float = Field(..., ge=0, le=50, description="Annual interest rate percentage")
    tenure_years: int = Field(..., gt=0, le=30, description="Repayment tenure in years")

    model_config = ConfigDict(from_attributes=True)

class EMICalculationResponse(BaseModel):
    amount: float
    rate: float
    tenure_years: int
    monthly_instalment: float
    quarterly_instalment: float
    total_interest: float
    total_payment: float

    model_config = ConfigDict(from_attributes=True)

def compute_emi(amount: float, rate: float, tenure_years: int) -> EMICalculationResponse:
    monthly_rate = (rate / 12.0) / 100.0
    total_months = tenure_years * 12

    if monthly_rate > 0:
        emi_monthly = (amount * monthly_rate * math.pow(1.0 + monthly_rate, total_months)) / (math.pow(1.0 + monthly_rate, total_months) - 1.0)
    else:
        emi_monthly = amount / total_months

    emi_quarterly = emi_monthly * 3.0
    total_payment = emi_monthly * total_months
    total_interest = total_payment - amount

    return EMICalculationResponse(
        amount=round(amount, 2),
        rate=round(rate, 2),
        tenure_years=tenure_years,
        monthly_instalment=round(emi_monthly, 2),
        quarterly_instalment=round(emi_quarterly, 2),
        total_interest=round(total_interest, 2),
        total_payment=round(total_payment, 2)
    )

@router.post("/calculate", response_model=EMICalculationResponse)
def calculate_emi_post(req: EMICalculationRequest):
    """Calculate monthly & quarterly EMI repayments via POST request."""
    return compute_emi(req.amount, req.rate, req.tenure_years)

@router.get("/calculate", response_model=EMICalculationResponse)
def calculate_emi_get(
    amount: float = Query(125000.0, gt=0),
    rate: float = Query(6.5, ge=0, le=50.0),
    tenure_years: int = Query(3, gt=0, le=30)
):
    """Calculate monthly & quarterly EMI repayments via GET query parameters."""
    return compute_emi(amount, rate, tenure_years)
