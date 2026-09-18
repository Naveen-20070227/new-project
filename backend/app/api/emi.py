import csv
import math
import os
import re
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict

router = APIRouter(prefix="/emi", tags=["EMI Calculator"])

CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "seed", "nsfdc_schemes.csv")

class CalculationRequest(BaseModel):
    principal: Optional[float] = Field(None, description="Principal loan amount in INR")
    amount: Optional[float] = Field(None, description="Alias for principal loan amount")
    rate: float = Field(..., ge=0, le=50, description="Annual interest rate percentage")
    tenure: Optional[int] = Field(None, description="Repayment tenure value")
    tenure_years: Optional[int] = Field(None, description="Repayment tenure in years")
    tenure_type: Optional[str] = Field("months", description="'months' or 'years'")
    scheme_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class CalculationResponse(BaseModel):
    principal: float
    rate: float
    tenure_months: int
    monthly_emi: float
    total_interest: float
    total_payable: float
    formatted_emi: str
    formatted_interest: str
    formatted_payable: str
    
    # Backward Compatibility Fields for tests and existing API consumers
    amount: float
    tenure_years: int
    monthly_instalment: float
    quarterly_instalment: float
    total_payment: float

    model_config = ConfigDict(from_attributes=True)

def parse_schemes_from_csv() -> List[dict]:
    schemes = []
    seen_ids = set()

    if not os.path.exists(CSV_FILE_PATH):
        fallback = [
            {"id": "SCHEME_001", "name": "Micro Finance Scheme (MFS)", "rate": 6.5},
            {"id": "SCHEME_002", "name": "Term Loan", "rate": 8.0},
            {"id": "SCHEME_003", "name": "Aajeevika Micro-Finance", "rate": 15.0},
            {"id": "SCHEME_004_1", "name": "Udyam Nidhi (Cooperative)", "rate": 13.0},
            {"id": "SCHEME_004_2", "name": "Udyam Nidhi (SFBs)", "rate": 15.0},
            {"id": "SCHEME_005", "name": "Educational Loan Scheme", "rate": 6.5}
        ]
        return fallback

    with open(CSV_FILE_PATH, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            s_id = row.get("scheme_id", "").strip()
            s_name = row.get("scheme_name", "").strip()
            rate_str = row.get("beneficiary_interest_rate", "").strip()
            
            if ";" in rate_str:
                parts = rate_str.split(";")
                for idx, part in enumerate(parts, 1):
                    sub_id = f"{s_id}_{idx}"
                    if sub_id in seen_ids:
                        continue
                    seen_ids.add(sub_id)
                    match = re.search(r"([\d\.]+)%", part)
                    rate_val = float(match.group(1)) if match else 10.0
                    sub_label = re.sub(r"[\d\.]*%", "", part).strip(" ()")
                    name_full = f"{s_name} ({sub_label})" if sub_label else f"{s_name} Option {idx}"
                    schemes.append({
                        "id": sub_id,
                        "name": name_full,
                        "rate": rate_val,
                        "scheme_type": row.get("scheme_type"),
                        "purpose": row.get("purpose"),
                        "maximum_loan_amount": row.get("maximum_loan_amount"),
                        "repayment_period": row.get("repayment_period"),
                        "moratorium_period": row.get("moratorium_period")
                    })
            else:
                if s_id in seen_ids:
                    continue
                seen_ids.add(s_id)
                match = re.search(r"([\d\.]+)%", rate_str)
                rate_val = float(match.group(1)) if match else 6.5
                schemes.append({
                    "id": s_id,
                    "name": s_name,
                    "rate": rate_val,
                    "scheme_type": row.get("scheme_type"),
                    "purpose": row.get("purpose"),
                    "maximum_loan_amount": row.get("maximum_loan_amount"),
                    "repayment_period": row.get("repayment_period"),
                    "moratorium_period": row.get("moratorium_period")
                })
    return schemes

def format_indian_currency(amount: float) -> str:
    rounded = int(round(amount))
    s = str(rounded)
    if len(s) <= 3:
        return f"₹ {s}"
    last_three = s[-3:]
    other_digits = s[:-3]
    res = ""
    while len(other_digits) > 2:
        res = "," + other_digits[-2:] + res
        other_digits = other_digits[:-2]
    if other_digits:
        res = other_digits + res
    return f"₹ {res},{last_three}"

def compute_calculation(principal: float, rate: float, tenure_months: int) -> dict:
    if principal <= 0 or tenure_months <= 0:
        raise HTTPException(status_code=400, detail="Principal and tenure must be greater than zero.")

    if rate == 0:
        monthly_emi = principal / tenure_months
    else:
        r = rate / 12 / 100
        n = tenure_months
        monthly_emi = (principal * r * math.pow(1 + r, n)) / (math.pow(1 + r, n) - 1)

    total_payable = monthly_emi * tenure_months
    total_interest = total_payable - principal
    quarterly_instalment = monthly_emi * 3.0
    tenure_years = max(1, math.ceil(tenure_months / 12))

    return {
        "principal": round(principal, 2),
        "rate": round(rate, 2),
        "tenure_months": tenure_months,
        "monthly_emi": round(monthly_emi, 2),
        "total_interest": round(total_interest, 2),
        "total_payable": round(total_payable, 2),
        "formatted_emi": format_indian_currency(monthly_emi),
        "formatted_interest": format_indian_currency(total_interest),
        "formatted_payable": format_indian_currency(total_payable),
        "amount": round(principal, 2),
        "tenure_years": tenure_years,
        "monthly_instalment": round(monthly_emi, 2),
        "quarterly_instalment": round(quarterly_instalment, 2),
        "total_payment": round(total_payable, 2)
    }

@router.get("/schemes")
def get_emi_schemes():
    return parse_schemes_from_csv()

@router.post("/calculate", response_model=CalculationResponse)
def calculate_emi_post(data: CalculationRequest):
    p = data.principal if data.principal is not None else (data.amount if data.amount is not None else 100000.0)
    
    if data.tenure_years is not None and data.tenure is None:
        tenure_months = data.tenure_years * 12
    else:
        t_val = data.tenure if data.tenure is not None else 36
        tenure_months = t_val * 12 if data.tenure_type == 'years' else t_val

    return compute_calculation(p, data.rate, tenure_months)

@router.get("/calculate", response_model=CalculationResponse)
def calculate_emi_get(
    amount: float = Query(125000.0, gt=0),
    principal: Optional[float] = Query(None, gt=0),
    rate: float = Query(6.5, ge=0, le=50.0),
    tenure_years: Optional[int] = Query(None, gt=0, le=30),
    tenure: Optional[int] = Query(None, gt=0),
    tenure_type: Optional[str] = Query("months")
):
    p = principal if principal is not None else amount
    if tenure_years is not None and tenure is None:
        tenure_months = tenure_years * 12
    else:
        t_val = tenure if tenure is not None else 36
        tenure_months = t_val * 12 if tenure_type == 'years' else t_val

    return compute_calculation(p, rate, tenure_months)
