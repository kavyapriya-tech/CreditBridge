"""
CreditBridge - Explainability Module
--------------------------------------
For a trained Logistic Regression pipeline, computes the top
contributing factors for a single applicant's prediction.

This is REAL model evidence (coefficient x scaled feature value),
not an invented explanation.
"""

import joblib
import numpy as np
import pandas as pd

# Human-readable labels for each raw feature
FEATURE_LABELS = {
    "monthly_income": "Monthly income",
    "income_stability_score": "Income stability",
    "avg_monthly_txn_volatility": "Spending volatility",
    "credit_history_months": "Length of credit history",
    "utility_payment_consistency": "Utility/rent payment consistency",
    "existing_monthly_debt": "Existing monthly debt",
    "savings_to_income_ratio": "Savings relative to income",
    "num_dependents": "Number of dependents",
    "debt_to_income_ratio": "Debt-to-income ratio",
}

RISK_LABELS = {0: "Low", 1: "Medium", 2: "High"}


def load_model(path="risk_model.joblib"):
    return joblib.load(path)


def explain_applicant(pipeline, applicant_df: pd.DataFrame, top_n=5):
    """
    applicant_df: a single-row DataFrame with the same raw columns used in training
    Returns: dict with risk_label, risk_category, probabilities, and top factors
    """
    preprocessor = pipeline.named_steps["preprocessor"]
    classifier = pipeline.named_steps["classifier"]

    # Predict
    pred_class = int(pipeline.predict(applicant_df)[0])
    pred_proba = pipeline.predict_proba(applicant_df)[0]

    # Transform features the same way the model saw them during training
    X_transformed = preprocessor.transform(applicant_df)
    if hasattr(X_transformed, "toarray"):
        X_transformed = X_transformed.toarray()
    X_transformed = X_transformed[0]

    # Get feature names after preprocessing (numeric + one-hot encoded categorical)
    feature_names = preprocessor.get_feature_names_out()

    # Coefficients for the predicted class
    coefs = classifier.coef_[pred_class]

    # Contribution = coefficient * transformed feature value
    contributions = coefs * X_transformed

    # Build a readable list of (feature, contribution, direction)
    factor_list = []
    for fname, contrib in zip(feature_names, contributions):
        clean_name = fname.split("__")[-1]
        # map onehot columns like employment_type_gig_worker back to a label
        base_label = None
        for raw_key, label in FEATURE_LABELS.items():
            if clean_name.startswith(raw_key):
                base_label = label
                break
        if base_label is None:
            base_label = clean_name.replace("_", " ").title()

        factor_list.append({
            "factor": base_label,
            "contribution": float(contrib),
            "direction": (
                f"supports {RISK_LABELS[pred_class]} risk classification" if contrib > 0
                else f"works against {RISK_LABELS[pred_class]} risk classification"
            ),
        })
    # Sort by absolute contribution, take top N
    factor_list.sort(key=lambda x: abs(x["contribution"]), reverse=True)
    top_factors = factor_list[:top_n]

    return {
        "risk_label": pred_class,
        "risk_category": RISK_LABELS[pred_class],
        "probabilities": {
            RISK_LABELS[i]: float(round(p, 4)) for i, p in enumerate(pred_proba)
        },
        "top_factors": top_factors,
    }


if __name__ == "__main__":
    # Quick manual test using one row from the dataset
    pipeline = load_model()
    df = pd.read_csv("applicants_synthetic.csv")
    sample = df.drop(columns=["risk_label"]).iloc[[10]]  # one applicant

    result = explain_applicant(pipeline, sample)

    print("Prediction for sample applicant:")
    print(f"Risk category: {result['risk_category']}")
    print(f"Probabilities: {result['probabilities']}")
    print("\nTop contributing factors:")
    for f in result["top_factors"]:
        print(f"  - {f['factor']}: {f['direction']} (weight: {f['contribution']:.4f})")