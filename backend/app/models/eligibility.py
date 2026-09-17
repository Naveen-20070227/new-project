from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from backend.app.core.database import Base

class EligibilityCheck(Base):
    __tablename__ = "eligibility_checks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    annual_income = Column(Float, nullable=False)
    amount_required = Column(Float, nullable=False)
    product_cost = Column(Float, nullable=False)
    loan_type = Column(String(50), nullable=False) # Business or Education
    
    # Business loan fields
    purpose = Column(String(255), nullable=True)
    unit = Column(String(50), nullable=True) # New or Expanding
    business_description = Column(Text, nullable=True)
    
    # Education loan fields
    course_name = Column(String(255), nullable=True)
    college_name = Column(String(255), nullable=True)
    number_of_years = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
