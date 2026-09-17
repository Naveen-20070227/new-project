from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.scheme import Scheme
from backend.app.schemas.scheme import SchemeResponse

router = APIRouter(prefix="/schemes", tags=["Schemes"])

@router.get("", response_model=List[SchemeResponse])
def get_all_schemes(db: Session = Depends(get_db)):
    """Retrieve all government loan schemes stored in SQLite."""
    schemes = db.query(Scheme).all()
    return schemes

@router.get("/{scheme_id}", response_model=SchemeResponse)
def get_scheme_by_id(scheme_id: str, db: Session = Depends(get_db)):
    """Retrieve scheme details by DB ID or scheme code."""
    if scheme_id.isdigit():
        scheme = db.query(Scheme).filter(Scheme.id == int(scheme_id)).first()
    else:
        scheme = db.query(Scheme).filter(Scheme.code == scheme_id.upper()).first()
        
    if not scheme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme '{scheme_id}' not found in database."
        )
    return scheme
