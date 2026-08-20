"""
CreditBridge - Model Training Script
--------------------------------------
Trains and compares two models (Logistic Regression, Random Forest)
on the synthetic applicant dataset, picks the better one by ROC-AUC,
and saves it for use by the backend API.
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)

# ---- 1. Load data ----
df = pd.read_csv("applicants_synthetic.csv")

X = df.drop(columns=["risk_label"])
y = df["risk_label"]

numeric_features = [
    "monthly_income", "income_stability_score", "avg_monthly_txn_volatility",
    "credit_history_months", "utility_payment_consistency", "existing_monthly_debt",
    "savings_to_income_ratio", "num_dependents", "debt_to_income_ratio"
]
categorical_features = ["employment_type"]

# ---- 2. Train/test split BEFORE any preprocessing (avoid leakage) ----
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ---- 3. Preprocessing pipeline ----
preprocessor = ColumnTransformer(transformers=[
    ("num", StandardScaler(), numeric_features),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
])

# ---- 4. Candidate models ----
models = {
    "logistic_regression": LogisticRegression(max_iter=1000),
    "random_forest": RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42),
}

results = {}
fitted_pipelines = {}

for name, model in models.items():
    pipe = Pipeline(steps=[("preprocessor", preprocessor), ("classifier", model)])
    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)
    y_proba = pipe.predict_proba(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="macro")
    rec = recall_score(y_test, y_pred, average="macro")
    f1 = f1_score(y_test, y_pred, average="macro")
    auc = roc_auc_score(y_test, y_proba, multi_class="ovr")

    results[name] = {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1, "roc_auc": auc}
    fitted_pipelines[name] = pipe

    print(f"\n{'='*50}")
    print(f"Model: {name}")
    print(f"{'='*50}")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"ROC-AUC:   {auc:.4f}")
    print("\nConfusion Matrix (rows=actual, cols=predicted):")
    print(confusion_matrix(y_test, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Low", "Medium", "High"]))

# ---- 5. Pick best model by ROC-AUC ----
best_model_name = max(results, key=lambda k: results[k]["roc_auc"])
best_pipeline = fitted_pipelines[best_model_name]

print(f"\n{'='*50}")
print(f"BEST MODEL: {best_model_name} (ROC-AUC: {results[best_model_name]['roc_auc']:.4f})")
print(f"{'='*50}")

# ---- 6. Save the best model ----
joblib.dump(best_pipeline, "risk_model.joblib")
print("\nSaved best model to risk_model.joblib")

# Save metrics for documentation / PPT (real numbers, not fabricated)
metrics_df = pd.DataFrame(results).T
metrics_df.to_csv("model_metrics.csv")
print("Saved metrics to model_metrics.csv")