from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.user import User
from backend.app.models.profile import UserProfile
from backend.app.schemas.profile import ProfileCreateUpdate, ProfileResponse

router = APIRouter(prefix="/profile", tags=["User Profile"])

@router.get("", response_model=ProfileResponse)
def get_profile_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve authenticated user's SC profile."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(
            user_id=current_user.id,
            name=current_user.beneficiary_name,
            age=28,
            gender="Male",
            caste="SC",
            area="Rural",
            district="District Office",
            state="State Office"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        name=profile.name,
        age=profile.age,
        gender=profile.gender,
        caste=profile.caste,
        area=profile.area,
        district=profile.district,
        state=profile.state,
        mobile_number=current_user.mobile_number
    )

@router.post("", response_model=ProfileResponse)
@router.put("", response_model=ProfileResponse)
def create_or_update_profile_endpoint(
    req: ProfileCreateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update beneficiary profile. Caste is enforced as SC."""
    if req.caste.strip().upper() != "SC":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yojana.ai platform is specifically designed for SC (Scheduled Caste) beneficiaries."
        )
        
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(
            user_id=current_user.id,
            name=req.name.strip(),
            age=req.age,
            gender=req.gender.strip(),
            caste="SC",
            area=req.area.strip(),
            district=req.district.strip(),
            state=req.state.strip()
        )
        db.add(profile)
    else:
        profile.name = req.name.strip()
        profile.age = req.age
        profile.gender = req.gender.strip()
        profile.caste = "SC"
        profile.area = req.area.strip()
        profile.district = req.district.strip()
        profile.state = req.state.strip()
        
    db.commit()
    db.refresh(profile)

    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        name=profile.name,
        age=profile.age,
        gender=profile.gender,
        caste=profile.caste,
        area=profile.area,
        district=profile.district,
        state=profile.state,
        mobile_number=current_user.mobile_number
    )
