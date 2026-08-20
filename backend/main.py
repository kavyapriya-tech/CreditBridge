"""
CreditBridge - Main FastAPI application
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator
from typing import List

from database import engine, get_db, Base
import models
from risk_service import assess_applicant

# Create DB tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CreditBridge API")

# Allow the React frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Request/response schemas ----
VALID_EMPLOYMENT_TYPES = {"salaried", "self_employed", "gig_worker", "unemployed"}


class ApplicantIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    monthly_income: float = Field(..., ge=0, le=10_000_000)
    income_stability_score: float = Field(..., ge=0, le=1)
    employment_type: str
    avg_monthly_txn_volatility: float = Field(..., ge=0, le=1)
    credit_history_months: int = Field(..., ge=0, le=600)
    utility_payment_consistency: float = Field(..., ge=0, le=1)
    existing_monthly_debt: float = Field(..., ge=0, le=10_000_000)
    savings_to_income_ratio: float = Field(..., ge=0, le=1)
    num_dependents: int = Field(..., ge=0, le=20)

    @field_validator("employment_type")
    @classmethod
    def validate_employment_type(cls, v):
        if v not in VALID_EMPLOYMENT_TYPES:
            raise ValueError(f"employment_type must be one of {VALID_EMPLOYMENT_TYPES}")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("name cannot be blank")
        return v.strip()


class AssessmentOut(BaseModel):
    applicant_id: int
    applicant_name: str
    risk_label: int
    risk_category: str
    probabilities: dict
    top_factors: list


# ---- Endpoints ----

@app.get("/")
def root():
    return {"status": "CreditBridge API is running"}


@app.post("/api/assessments", response_model=AssessmentOut)
def create_assessment(applicant: ApplicantIn, db: Session = Depends(get_db)):
    # 1. Save applicant to DB
    db_applicant = models.Applicant(**applicant.model_dump())
    db.add(db_applicant)
    db.commit()
    db.refresh(db_applicant)

    # 2. Run risk assessment
    try:
        result = assess_applicant(applicant.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")

    # 3. Save assessment result
    db_assessment = models.Assessment(
        applicant_id=db_applicant.id,
        risk_label=result["risk_label"],
        risk_category=result["risk_category"],
        probabilities=result["probabilities"],
        top_factors=result["top_factors"],
    )
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)

    return AssessmentOut(
        applicant_id=db_applicant.id,
        applicant_name=db_applicant.name,
        risk_label=result["risk_label"],
        risk_category=result["risk_category"],
        probabilities=result["probabilities"],
        top_factors=result["top_factors"],
    )


@app.get("/api/assessments")
def list_assessments(db: Session = Depends(get_db)):
    assessments = db.query(models.Assessment).order_by(models.Assessment.created_at.desc()).all()
    results = []
    for a in assessments:
        applicant = db.query(models.Applicant).filter(models.Applicant.id == a.applicant_id).first()
        results.append({
            "assessment_id": a.id,
            "applicant_id": a.applicant_id,
            "applicant_name": applicant.name if applicant else "Unknown",
            "risk_category": a.risk_category,
            "risk_label": a.risk_label,
            "created_at": a.created_at,
        })
    return results


@app.get("/api/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    total = db.query(models.Assessment).count()
    low = db.query(models.Assessment).filter(models.Assessment.risk_label == 0).count()
    medium = db.query(models.Assessment).filter(models.Assessment.risk_label == 1).count()
    high = db.query(models.Assessment).filter(models.Assessment.risk_label == 2).count()
    return {"total": total, "low_risk": low, "medium_risk": medium, "high_risk": high}