"""
CreditBridge - Risk assessment service
Wraps model loading + prediction + explanation for use by the API.
"""

import pandas as pd
from explain import load_model, explain_applicant

# Load model once at startup (not per-request, for performance)
_pipeline = load_model("risk_model.joblib")

REQUIRED_FIELDS = [
    "monthly_income", "income_stability_score", "employment_type",
    "avg_monthly_txn_volatility", "credit_history_months",
    "utility_payment_consistency", "existing_monthly_debt",
    "savings_to_income_ratio", "num_dependents",
]


def assess_applicant(applicant_data: dict) -> dict:
    """
    applicant_data: dict with the raw applicant fields (no risk_label)
    Returns: dict with risk_label, risk_category, probabilities, top_factors
    """
    row = {k: applicant_data[k] for k in REQUIRED_FIELDS}
    row["debt_to_income_ratio"] = round(
        row["existing_monthly_debt"] / max(row["monthly_income"], 1), 3
    )

    df = pd.DataFrame([row])
    result = explain_applicant(_pipeline, df)
    return result