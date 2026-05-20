# Retail Data Quality & Predictive Analytics Dashboard

End-to-end analytics workflow built in Python for cleaning retail data, documenting data quality issues, generating predictive insights, and presenting results through an interactive Streamlit dashboard.

This project demonstrates how raw business data can be transformed into clean, decision-ready output while preserving transparency and explainability.

---

# Dashboard Preview

## Main Dashboard

![Dashboard Overview](screenshots/dashboard_overview.png)

## Segment Risk Drilldown

![Segment Analysis](screenshots/segment_analysis.png)

## Data Quality Review

![Data Quality](screenshots/data_quality.png)

---

# Project Workflow

Raw Dataset (.csv)

↓

Data Cleaning Engine

↓

Quality Reports & Error Detection

↓

Predictive Analytics

↓

Interactive Dashboard

↓

Business Recommendations

---

# Features

## Data Cleaning

The cleaning engine performs:

- Original dataset preservation
- Clean dataset generation
- Duplicate detection
- Removal of unusable rows
- Missingness reporting
- Numeric summaries
- Human-readable text distributions
- Exact error tracking
- Cell-level issue identification
- Change logging

Generated outputs:

- Original_Data
- Cleaned_Data
- Change_Log
- Missingness
- Numeric_Summary
- Text_Distributions

---

## Predictive Analytics

The predictive workflow creates a transparent business risk model.

The model evaluates:

- Sales momentum
- Recency-weighted performance
- Sales volatility
- Relative sales strength
- Transaction volume
- Customer concentration risk
- Outlier burden
- Data reliability risk

Outputs include:

- Executive summary
- Model insights
- Risk score explanation
- Scientific breakdown
- Full risk model output

---

## Composite Risk Score (v2)

The model uses a transparent weighted scoring framework.

### Business Trend Risk (25%)

Evaluates:

- Sales momentum
- Recency weighting

### Operational Risk (20%)

Evaluates:

- Sales volatility
- Transaction volume

### Customer Risk (15%)

Evaluates:

- Customer concentration

### Performance Risk (20%)

Evaluates:

- Relative sales strength

### Data Reliability Risk (20%)

Evaluates:

- Outlier burden
- Data support quality

---

## Risk Score Interpretation

The composite risk score ranges from:

0 → Lowest relative concern

100 → Highest relative concern

The score is a **relative ranking metric**.

It is **NOT** a probability.

Example:

Risk Score = 60

Does NOT mean:

“60% chance of decline”

Instead it means:

“This segment ranked higher in relative risk compared with lower-scoring segments.”

Risk categories:

- Low Risk = 0–24.9
- Moderate Risk = 25–49.9
- High Risk = 50–74.9
- Critical Risk = 75–100

---

## Model Enhancements

Additional considerations included in the updated model:

- Recency weighting using exponential decay
- Customer dependency assessment
- Outlier burden evaluation
- Data reliability adjustment
- Expanded scientific documentation
- Business-friendly interpretation layer

The risk score is intended as an early warning indicator and should not be interpreted as probability.

---

## Dashboard

Interactive Streamlit dashboard includes:

### Executive View

- Data quality score
- Rows removed
- Issues detected
- Highest-risk segment

### Interactive Analytics

- Segment drilldown
- Risk drivers
- Missingness review
- Issue exploration
- Risk visualization

### Decision Support

- Business interpretation
- Recommended next actions
- Risk explanation
- Downloadable reports

Launch dashboard:

```bash
streamlit run dashboard.py
```