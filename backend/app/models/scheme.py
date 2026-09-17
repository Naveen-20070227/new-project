from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from backend.app.core.database import Base

class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False) # Business or Education
    target_cost_desc = Column(String(255), nullable=False)
    min_unit_cost = Column(Float, nullable=False, default=0.0)
    max_unit_cost = Column(Float, nullable=False, default=0.0) # 0 means no upper limit
    max_loan_pct = Column(Float, nullable=False, default=90.0)
    min_loan_amount = Column(Float, nullable=False, default=0.0)
    max_loan_amount = Column(Float, nullable=False, default=0.0)
    beneficiary_interest_rate = Column(Float, nullable=False) # e.g. 6.5
    beneficiary_interest_rate_desc = Column(String(100), nullable=False)
    intermediary_rate = Column(String(100), nullable=True) # SCA/CA or NBFC rate
    repayment_desc = Column(String(255), nullable=False)
    max_repayment_years = Column(Float, nullable=False)
    moratorium_desc = Column(String(255), nullable=False)
    moratorium_months = Column(Integer, nullable=False, default=3)
    short_description = Column(Text, nullable=False)
    full_description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
