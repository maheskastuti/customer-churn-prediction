"""
generate_data.py
Generates a realistic synthetic telecom customer dataset for churn prediction.
Mimics the structure of common industry churn datasets (e.g. tenure, contract
type, monthly charges, support interactions) with genuine, learnable churn
signal baked into the generating process.
"""

import numpy as np
import pandas as pd

np.random.seed(42)

N = 5000

customer_id = [f"CUST{100000+i}" for i in range(N)]

gender = np.random.choice(["Male", "Female"], N)
senior_citizen = np.random.choice([0, 1], N, p=[0.84, 0.16])
partner = np.random.choice(["Yes", "No"], N, p=[0.48, 0.52])
dependents = np.random.choice(["Yes", "No"], N, p=[0.30, 0.70])

tenure_months = np.random.gamma(shape=2.0, scale=15, size=N).astype(int)
tenure_months = np.clip(tenure_months, 0, 72)

contract = np.random.choice(
    ["Month-to-month", "One year", "Two year"], N, p=[0.55, 0.24, 0.21]
)

internet_service = np.random.choice(
    ["Fiber optic", "DSL", "No"], N, p=[0.44, 0.34, 0.22]
)

payment_method = np.random.choice(
    ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
    N, p=[0.34, 0.23, 0.22, 0.21]
)

paperless_billing = np.random.choice(["Yes", "No"], N, p=[0.59, 0.41])

tech_support = np.random.choice(["Yes", "No", "No internet service"], N, p=[0.29, 0.49, 0.22])
online_security = np.random.choice(["Yes", "No", "No internet service"], N, p=[0.29, 0.49, 0.22])
streaming_tv = np.random.choice(["Yes", "No", "No internet service"], N, p=[0.38, 0.40, 0.22])

# Monthly charges depend on internet service type
base_charge = np.where(internet_service == "Fiber optic", 75,
              np.where(internet_service == "DSL", 55, 25))
monthly_charges = base_charge + np.random.normal(0, 12, N)
monthly_charges = np.clip(monthly_charges, 18, 120).round(2)

total_charges = (monthly_charges * tenure_months + np.random.normal(0, 50, N)).clip(min=0).round(2)

num_support_calls = np.random.poisson(1.5, N)
num_support_calls = np.clip(num_support_calls, 0, 10)

# --- Build churn probability from realistic risk factors ---
churn_logit = (
    -1.9
    + 1.85 * (contract == "Month-to-month")
    + 0.55 * (contract == "One year")
    + 0.85 * (payment_method == "Electronic check")
    - 0.45 * (payment_method == "Credit card (automatic)")
    - 0.40 * (payment_method == "Bank transfer (automatic)")
    + 0.025 * (monthly_charges - 60)
    - 0.05 * tenure_months
    + 0.32 * num_support_calls
    + 0.65 * (tech_support == "No")
    + 0.45 * (online_security == "No")
    + 0.25 * (internet_service == "Fiber optic")
    - 0.30 * (partner == "Yes")
    - 0.20 * (dependents == "Yes")
    + 0.30 * (senior_citizen == 1)
    + np.random.normal(0, 0.12, N)  # reduced noise -> stronger learnable signal
)
churn_logit = churn_logit * 1.35

churn_prob = 1 / (1 + np.exp(-churn_logit))
churn = np.where(churn_prob > np.random.uniform(0, 1, N), "Yes", "No")

df = pd.DataFrame({
    "customerID": customer_id,
    "gender": gender,
    "SeniorCitizen": senior_citizen,
    "Partner": partner,
    "Dependents": dependents,
    "tenure": tenure_months,
    "Contract": contract,
    "InternetService": internet_service,
    "PaymentMethod": payment_method,
    "PaperlessBilling": paperless_billing,
    "TechSupport": tech_support,
    "OnlineSecurity": online_security,
    "StreamingTV": streaming_tv,
    "NumSupportCalls": num_support_calls,
    "MonthlyCharges": monthly_charges,
    "TotalCharges": total_charges,
    "Churn": churn,
})

df.to_csv("/home/claude/churn-project/data/customer_churn_data.csv", index=False)
print(f"Generated {len(df)} rows")
print(df["Churn"].value_counts(normalize=True))
