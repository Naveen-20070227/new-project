from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class RecommendedSchemeItem(BaseModel):
    rank: int
    scheme_id: str
    scheme_name: str
    suitability_score: float
    why_recommended: List[str]
    important_conditions: List[str]
    max_loan_desc: str
    interest_rate_desc: str
    repayment_desc: str
    moratorium_desc: str

class FinalRecommendation(BaseModel):
    scheme_id: str
    scheme_name: str
    reason: str

class RecommendationResponse(BaseModel):
    check_id: int
    applicant_summary: Dict[str, Any]
    eligibility_status: Dict[str, List[Any]] # eligible, ineligible, requires_information
    suitability_analysis: List[Dict[str, Any]]
    recommendations: List[RecommendedSchemeItem]
    final_recommendation: Optional[FinalRecommendation] = None
    ai_available: bool = True
    ai_error_message: Optional[str] = None
    disclaimer: str
