from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.user import User
from backend.app.schemas.eligibility import CheckEligibilityRequest, ValidationResult
from backend.app.schemas.recommendation import RecommendationResponse
from backend.app.services.validation_service import validate_applicant_data
from backend.app.services.recommendation_service import process_eligibility_and_recommendation

router = APIRouter(prefix="/eligibility", tags=["Eligibility & Recommendation Engine"])

@router.post("/validate", response_model=ValidationResult)
def validate_eligibility_input_endpoint(req: CheckEligibilityRequest):
    """Validate applicant requirements without triggering recommendations."""
    return validate_applicant_data(req)

@router.post("/check", response_model=RecommendationResponse)
def check_eligibility_and_recommend_endpoint(
    req: CheckEligibilityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Main eligibility check & AI recommendation pipeline.
    Validates input -> Preprocesses -> Rule-Based Eligibility Engine -> Feature Analysis -> OpenAI AI Recommendation -> Persistence.
    """
    try:
        return process_eligibility_and_recommendation(db, current_user.id, req)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing eligibility recommendation: {str(err)}"
        )
