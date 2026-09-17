from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class LLMRecommendationItem(BaseModel):
    rank: int
    scheme_id: str
    scheme_name: str
    suitability_score: float
    why_recommended: List[str]
    important_conditions: List[str]

class LLMFinalRecommendation(BaseModel):
    scheme_id: str
    scheme_name: str
    reason: str

class LLMRecommendationOutput(BaseModel):
    applicant_summary: Dict[str, Any]
    eligibility_status: Dict[str, List[Any]]
    suitability_analysis: List[Dict[str, Any]]
    recommendations: List[LLMRecommendationItem]
    final_recommendation: LLMFinalRecommendation
    alternative_options: List[Dict[str, Any]] = []
    missing_information: List[str] = []
    limitations: List[str] = []
