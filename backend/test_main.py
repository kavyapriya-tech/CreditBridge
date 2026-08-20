"""
CreditBridge - Basic backend tests
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

VALID_APPLICANT = {
    "name": "Test Applicant",
    "monthly_income": 40000,
    "income_stability_score": 0.7,
    "employment_type": "salaried",
    "avg_monthly_txn_volatility": 0.3,
    "credit_history_months": 24,
    "utility_payment_consistency": 0.8,
    "existing_monthly_debt": 5000,
    "savings_to_income_ratio": 0.2,
    "num_dependents": 1,
}


def test_root_endpoint():
    """API root should respond with a status message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "CreditBridge API is running"


def test_create_assessment_valid_applicant():
    """A valid applicant should be scored and return a risk category."""
    response = client.post("/api/assessments", json=VALID_APPLICANT)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_category"] in ("Low", "Medium", "High")
    assert "top_factors" in data
    assert len(data["top_factors"]) > 0


def test_create_assessment_rejects_invalid_data():
    """Invalid applicant data should be rejected with a 422, not saved."""
    bad_applicant = VALID_APPLICANT.copy()
    bad_applicant["name"] = ""
    bad_applicant["monthly_income"] = -500
    bad_applicant["employment_type"] = "not_a_real_type"

    response = client.post("/api/assessments", json=bad_applicant)
    assert response.status_code == 422


def test_dashboard_summary_returns_counts():
    """Dashboard summary should return numeric counts for each risk category."""
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "low_risk" in data
    assert "medium_risk" in data
    assert "high_risk" in data
    assert isinstance(data["total"], int)