"""
CreditBridge - Synthetic Dataset Generator
--------------------------------------------
This creates a REALISTIC but ARTIFICIAL dataset for demonstrating
dynamic risk assessment for underserved/underbanked applicants.

No real applicant data is used anywhere in this project.
"""

import numpy as np
import pandas as pd

np.random.seed(42)  # reproducibility

N = 3000  # number of synthetic applicants

employment_types = ["salaried", "self_employed", "gig_worker", "unemployed"]
employment_probs = [0.45, 0.25, 0.20, 0.10]

df = pd.DataFrame({
    "monthly_income": np.round(np.random.gamma(shape=4, scale=8000, size=N), -2),
    "income_stability_score": np.clip(np.random.beta(5, 2, N), 0, 1),
    "employment_type": np.random.choice(employment_types, size=N, p=employment_probs),
    "avg_monthly_txn_volatility": np.clip(np.random.beta(2, 5, N), 0, 1),
    "credit_history_months": np.random.exponential(scale=24, size=N).astype(int),
    "utility_payment_consistency": np.clip(np.random.beta(6, 2, N), 0, 1),
    "existing_monthly_debt": np.round(np.random.gamma(shape=2, scale=3000, size=N), -2),
    "savings_to_income_ratio": np.clip(np.random.beta(2, 6, N), 0, 1),
    "num_dependents": np.random.poisson(1.2, size=N),
})

df["credit_history_months"] = df["credit_history_months"].clip(0, 240)
df["debt_to_income_ratio"] = np.round(
    df["existing_monthly_debt"] / df["monthly_income"].replace(0, 1), 3
)

employment_risk_map = {"salaried": 0.0, "self_employed": 0.15, "gig_worker": 0.25, "unemployed": 0.5}
df["employment_risk"] = df["employment_type"].map(employment_risk_map)

raw_risk = (
    0.25 * (1 - df["income_stability_score"])
    + 0.20 * df["avg_monthly_txn_volatility"]
    + 0.15 * (1 - df["utility_payment_consistency"])
    + 0.20 * df["debt_to_income_ratio"].clip(0, 2) / 2
    + 0.10 * df["employment_risk"]
    + 0.10 * (1 - df["savings_to_income_ratio"])
)

raw_risk = raw_risk + np.random.normal(0, 0.03, size=N)
raw_risk = np.clip(raw_risk, 0, 1)

df["risk_raw_score"] = np.round(raw_risk, 3)

# Use percentile-based cutoffs so all 3 risk categories are realistically represented
low_cut = df["risk_raw_score"].quantile(0.55)
high_cut = df["risk_raw_score"].quantile(0.85)

df["risk_label"] = pd.cut(
    df["risk_raw_score"],
    bins=[-0.01, low_cut, high_cut, 1.0],
    labels=[0, 1, 2]
).astype(int)

df_model = df.drop(columns=["employment_risk", "risk_raw_score"])

df_model.to_csv("applicants_synthetic.csv", index=False)

print("Dataset generated: applicants_synthetic.csv")
print(f"Rows: {len(df_model)}")
print("\nRisk label distribution:")
print(df_model["risk_label"].value_counts().sort_index())
print("\nFirst 5 rows:")
print(df_model.head())