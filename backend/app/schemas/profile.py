from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class ProfileCreateUpdate(BaseModel):
    name: str = Field(..., min_length=2)
    age: int = Field(..., ge=18, le=75)
    gender: str = Field(..., description="Male, Female, Transgender, Other")
    caste: str = Field("SC", description="Must be SC for beneficiaries")
    area: str = Field(..., description="Rural or Urban")
    district: str = Field(..., min_length=2)
    state: str = Field(..., min_length=2)

class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    age: int
    gender: str
    caste: str
    area: str
    district: str
    state: str
    mobile_number: Optional[str] = None


