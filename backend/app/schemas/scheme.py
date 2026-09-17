from pydantic import BaseModel, ConfigDict
from typing import Optional

class SchemeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    category: str
    target_cost_desc: str
    min_unit_cost: float
    max_unit_cost: float
    max_loan_pct: float
    min_loan_amount: float
    max_loan_amount: float
    beneficiary_interest_rate: float
    beneficiary_interest_rate_desc: str
    intermediary_rate: Optional[str] = None
    repayment_desc: str
    max_repayment_years: float
    moratorium_desc: str
    moratorium_months: int
    short_description: str
    full_description: str

