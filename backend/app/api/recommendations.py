import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.user import User
from backend.app.models.recommendation import Recommendation

router = APIRouter(prefix="/recommendations", tags=["Recommendations History"])

@router.get("/user/history")
def get_user_recommendation_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all recommendation history entries for the authenticated beneficiary."""
    records = db.query(Recommendation).filter(Recommendation.user_id == current_user.id).order_by(Recommendation.created_at.desc()).all()
    history = []
    for r in records:
        parsed = json.loads(r.full_response_json)
        created_str = r.created_at.isoformat() if r.created_at else ""
        if created_str and not created_str.endswith("Z") and "+" not in created_str:
            created_str += "Z"
        history.append({
            "recommendation_id": r.id,
            "check_id": r.check_id,
            "rank_1_scheme_code": r.rank_1_scheme_code,
            "rank_1_suitability_score": r.rank_1_suitability_score,
            "created_at": created_str,
            "applicant_summary": parsed.get("applicant_summary"),
            "final_recommendation": parsed.get("final_recommendation")
        })
    return history

@router.get("/{check_id}")
def get_recommendation_by_check_id(
    check_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve detailed recommendation output by Check ID."""
    rec = db.query(Recommendation).filter(
        Recommendation.check_id == check_id,
        Recommendation.user_id == current_user.id
    ).first()
    
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation record for check ID {check_id} not found."
        )
        
    return json.loads(rec.full_response_json)
