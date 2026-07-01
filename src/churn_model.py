"""
churn_model.py
Customer Churn Prediction — Logistic Regression pipeline.

Steps:
1. Load and clean raw customer data
2. Feature engineering (encoding categoricals, scaling numerics)
3. Train/test split
4. Train Logistic Regression model (scikit-learn)
5. Evaluate (accuracy, precision, recall, F1, confusion matrix)
6. Export scored dataset for Power BI dashboard
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)

DATA_PATH = "/home/claude/churn-project/data/customer_churn_data.csv"
OUT_DIR = "/home/claude/churn-project/dashboard"

# ---------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------
df = pd.read_csv(DATA_PATH)
print(f"Loaded {df.shape[0]} rows, {df.shape[1]} columns")

# ---------------------------------------------------------------
# 2. Data cleaning
# ---------------------------------------------------------------
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
df["TotalCharges"] = df["TotalCharges"].fillna(df["TotalCharges"].median())
df = df.drop_duplicates(subset="customerID")

# ---------------------------------------------------------------
# 3. Feature engineering
# ---------------------------------------------------------------
model_df = df.copy()

binary_cols = ["Partner", "Dependents", "PaperlessBilling"]
for col in binary_cols:
    model_df[col] = model_df[col].map({"Yes": 1, "No": 0})

model_df["gender"] = model_df["gender"].map({"Male": 1, "Female": 0})

three_way_cols = ["TechSupport", "OnlineSecurity", "StreamingTV"]
for col in three_way_cols:
    model_df[col] = model_df[col].map({"Yes": 1, "No": 0, "No internet service": 0})

categorical_cols = ["Contract", "InternetService", "PaymentMethod"]
model_df = pd.get_dummies(model_df, columns=categorical_cols, drop_first=True)

model_df["Churn"] = model_df["Churn"].map({"Yes": 1, "No": 0})

feature_cols = [c for c in model_df.columns if c not in ["customerID", "Churn"]]
X = model_df[feature_cols]
y = model_df["Churn"]

numeric_cols = ["tenure", "MonthlyCharges", "TotalCharges", "NumSupportCalls"]
scaler = StandardScaler()
X_scaled = X.copy()
X_scaled[numeric_cols] = scaler.fit_transform(X[numeric_cols])

# ---------------------------------------------------------------
# 4. Train / test split
# ---------------------------------------------------------------
X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
    X_scaled, y, model_df.index, test_size=0.2, random_state=42, stratify=y
)

# ---------------------------------------------------------------
# 5. Train Logistic Regression
# ---------------------------------------------------------------
model = LogisticRegression(max_iter=1000, C=0.5, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

# ---------------------------------------------------------------
# 6. Evaluation
# ---------------------------------------------------------------
acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_proba)
cm = confusion_matrix(y_test, y_pred)

print("\n--- Model Performance ---")
print(f"Accuracy : {acc:.4f}")
print(f"Precision: {prec:.4f}")
print(f"Recall   : {rec:.4f}")
print(f"F1 Score : {f1:.4f}")
print(f"ROC AUC  : {auc:.4f}")
print("\nConfusion Matrix:")
print(cm)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["No Churn", "Churn"]))

# ---------------------------------------------------------------
# 7. Feature importance (coefficients)
# ---------------------------------------------------------------
coef_df = pd.DataFrame({
    "Feature": feature_cols,
    "Coefficient": model.coef_[0]
}).sort_values("Coefficient", key=abs, ascending=False)

print("\nTop drivers of churn (by |coefficient|):")
print(coef_df.head(10).to_string(index=False))
coef_df.to_csv(f"{OUT_DIR}/feature_importance.csv", index=False)

# ---------------------------------------------------------------
# 8. Plots
# ---------------------------------------------------------------
plt.figure(figsize=(5, 4))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=["No Churn", "Churn"], yticklabels=["No Churn", "Churn"])
plt.ylabel("Actual")
plt.xlabel("Predicted")
plt.title("Confusion Matrix — Churn Prediction")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/confusion_matrix.png", dpi=150)
plt.close()

fpr, tpr, _ = roc_curve(y_test, y_proba)
plt.figure(figsize=(5, 4))
plt.plot(fpr, tpr, label=f"ROC Curve (AUC = {auc:.2f})", color="#2563eb")
plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve — Logistic Regression")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/roc_curve.png", dpi=150)
plt.close()

plt.figure(figsize=(6, 4))
top_feats = coef_df.head(10)
colors = ["#dc2626" if c > 0 else "#16a34a" for c in top_feats["Coefficient"]]
plt.barh(top_feats["Feature"], top_feats["Coefficient"], color=colors)
plt.xlabel("Coefficient (impact on churn log-odds)")
plt.title("Top 10 Churn Drivers")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/feature_importance.png", dpi=150)
plt.close()

# ---------------------------------------------------------------
# 9. Export scored dataset for Power BI
# ---------------------------------------------------------------
scored = df.loc[idx_test].copy()
scored["ChurnProbability"] = (y_proba * 100).round(2)
scored["PredictedChurn"] = np.where(y_pred == 1, "Yes", "No")
scored["ActualChurn"] = df.loc[idx_test, "Churn"]
scored["RiskSegment"] = pd.cut(
    scored["ChurnProbability"],
    bins=[0, 30, 60, 100],
    labels=["Low Risk", "Medium Risk", "High Risk"]
)

scored.to_csv(f"{OUT_DIR}/churn_scored_for_powerbi.csv", index=False)
print(f"\nExported scored dataset -> {OUT_DIR}/churn_scored_for_powerbi.csv")
print(f"Exported plots and feature importance -> {OUT_DIR}/")

# Save metrics summary
with open(f"{OUT_DIR}/model_metrics.txt", "w") as f:
    f.write("Customer Churn Prediction — Logistic Regression\n")
    f.write("=" * 50 + "\n")
    f.write(f"Accuracy : {acc:.4f}\n")
    f.write(f"Precision: {prec:.4f}\n")
    f.write(f"Recall   : {rec:.4f}\n")
    f.write(f"F1 Score : {f1:.4f}\n")
    f.write(f"ROC AUC  : {auc:.4f}\n")
    f.write("\nConfusion Matrix:\n")
    f.write(str(cm))
    f.write("\n\n")
    f.write(classification_report(y_test, y_pred, target_names=["No Churn", "Churn"]))
