# Power BI Dashboard — Build Guide

This guide walks you through building the interactive churn dashboard referenced in the project, using the model's output file: `dashboard/churn_scored_for_powerbi.csv`.

You'll need Power BI Desktop (free, Windows only — install from powerbi.microsoft.com if you don't have it).

## 1. Load the Data

1. Open Power BI Desktop → **Get Data** → **Text/CSV**
2. Select `dashboard/churn_scored_for_powerbi.csv`
3. Click **Transform Data** to open Power Query Editor
4. Set data types:
   - `ChurnProbability` → Decimal Number
   - `tenure`, `MonthlyCharges`, `TotalCharges`, `NumSupportCalls` → Decimal Number / Whole Number
   - `RiskSegment`, `PredictedChurn`, `ActualChurn`, `Contract`, `PaymentMethod` → Text
5. Click **Close & Apply**

## 2. Create DAX Measures

Go to **Modeling → New Measure** and add each of these:

```dax
Total Customers = COUNTROWS(churn_scored_for_powerbi)
```

```dax
Predicted Churners = 
CALCULATE(COUNTROWS(churn_scored_for_powerbi), churn_scored_for_powerbi[PredictedChurn] = "Yes")
```

```dax
Churn Rate % = 
DIVIDE([Predicted Churners], [Total Customers], 0) * 100
```

```dax
Avg Churn Probability = 
AVERAGE(churn_scored_for_powerbi[ChurnProbability])
```

```dax
High Risk Customers = 
CALCULATE(COUNTROWS(churn_scored_for_powerbi), churn_scored_for_powerbi[RiskSegment] = "High Risk")
```

```dax
Model Accuracy = 
DIVIDE(
    CALCULATE(COUNTROWS(churn_scored_for_powerbi), churn_scored_for_powerbi[PredictedChurn] = churn_scored_for_powerbi[ActualChurn]),
    [Total Customers], 0
) * 100
```

```dax
Avg Monthly Charges (Churners) = 
CALCULATE(AVERAGE(churn_scored_for_powerbi[MonthlyCharges]), churn_scored_for_powerbi[PredictedChurn] = "Yes")
```

```dax
Revenue at Risk = 
CALCULATE(SUM(churn_scored_for_powerbi[MonthlyCharges]), churn_scored_for_powerbi[RiskSegment] = "High Risk")
```

## 3. Build the Dashboard Pages

### Page 1 — Executive Summary
- **KPI Cards** (top row): `Total Customers`, `Churn Rate %`, `High Risk Customers`, `Revenue at Risk`
- **Donut chart**: `RiskSegment` (Low/Medium/High) — legend + count
- **Bar chart**: Churn Rate % by `Contract`
- **Bar chart**: Churn Rate % by `PaymentMethod`

### Page 2 — Customer Segments
- **Matrix visual**: Rows = `Contract`, Columns = `RiskSegment`, Values = Count of customers
- **Scatter plot**: `tenure` (x-axis) vs `MonthlyCharges` (y-axis), size = `ChurnProbability`, color = `RiskSegment`
- **Slicers**: `InternetService`, `SeniorCitizen`, `Contract`

### Page 3 — Model Insights
- **Table**: import `dashboard/feature_importance.csv` as a second data source, show top churn drivers
- **Bar chart**: Feature vs Coefficient (color positive/negative differently)
- **Card**: `Model Accuracy` measure
- **Gauge**: `Avg Churn Probability`

## 4. Formatting Tips

- Use a consistent color scheme: red/orange for high risk, green for low risk, matching `feature_importance.png` style
- Add a title text box: "Customer Churn Prediction Dashboard"
- Enable **Report Page Tooltips** on the scatter plot to show `customerID` on hover
- Add a slicer panel on the left, pinned across all pages using a bookmark or a **Sync Slicers** setup

## 5. Publish (optional)

If you have a Power BI account:
- **Home → Publish** → choose your workspace
- This gives you a shareable web link you can drop into your GitHub README or resume/portfolio

## 6. Save & Add to Repo

Once built, save as `dashboard/customer_churn_dashboard.pbix` and add it to your GitHub repo (or link a published Power BI web view if the file is too large for GitHub — files under 100MB are fine).

Optionally export a screenshot of the finished dashboard as `dashboard/dashboard_screenshot.png` and embed it in your README for anyone browsing the repo without Power BI installed.
