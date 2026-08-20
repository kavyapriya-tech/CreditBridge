"""
CreditBridge - Database table definitions
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from database import Base


class Applicant(Base):
    __tablename__ = "applicants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    monthly_income = Column(Float, nullable=False)
    income_stability_score = Column(Float, nullable=False)
    employment_type = Column(String, nullable=False)
    avg_monthly_txn_volatility = Column(Float, nullable=False)
    credit_history_months = Column(Integer, nullable=False)
    utility_payment_consistency = Column(Float, nullable=False)
    existing_monthly_debt = Column(Float, nullable=False)
    savings_to_income_ratio = Column(Float, nullable=False)
    num_dependents = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("applicants.id"), nullable=False)
    risk_label = Column(Integer, nullable=False)
    risk_category = Column(String, nullable=False)
    probabilities = Column(JSON, nullable=False)
    top_factors = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())