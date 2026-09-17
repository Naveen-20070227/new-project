from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from backend.app.core.database import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    check_id = Column(Integer, ForeignKey("eligibility_checks.id", ondelete="CASCADE"), nullable=False)
    
    rank_1_scheme_code = Column(String(50), nullable=True)
    rank_1_suitability_score = Column(Float, nullable=True)
    full_response_json = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
