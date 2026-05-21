# Retail Data Quality & Predictive Analytics Dashboard

End-to-end analytics workflow built in Python for cleaning retail data, documenting data quality issues, generating predictive insights, and presenting results through an interactive Streamlit dashboard.

This project demonstrates how raw business data can be transformed into clean, decision-ready output while preserving transparency, explainability, and production-style validation.

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

Raw Dataset (.csv / .xlsx)

↓

Configuration Layer (`config.json`)

↓

Validation Engine

↓

Data Cleaning Engine

↓

Quality Reports

↓

Predictive Analytics

↓

Interactive Dashboard

↓

Business Recommendations

---

# Features

## Configurable Inputs

The project uses:

```text
config.json
```

Users can define:

- Input file location
- Output files
- Date column
- Sales column
- Category column
- Customer column
- Unit columns

No code changes required when column names differ.

---

## Validation Layer

Centralized validation through:

```text
validation.py
```

Checks include:

- Missing config fields
- Missing required mappings
- Duplicate mappings
- Invalid input paths
- Unsupported file types
- Missing datasets

---

## Data Cleaning

Cleaning engine performs:

- Original dataset preservation
- Clean dataset generation
- Duplicate detection
- Invalid numeric removal
- Date validation
- Missingness reporting
- Numeric summaries
- Human-readable distributions
- Exact issue logging
- Cell-level tracking

Generated outputs:

- Original_Data
- Cleaned_Data
- Change_Log
- Missingness
- Numeric_Summary
- Text_Distributions

---

## Predictive Analytics

Transparent business risk model evaluates:

- Sales momentum
- Recency-weighted performance
- Sales volatility
- Relative sales strength
- Transaction volume
- Customer concentration
- Outlier burden
- Data reliability

Outputs include:

- Executive summary
- Model insights
- Scientific breakdown
- Risk score explanation
- Full model output

---

# Composite Risk Score (v2)

Business Trend Risk (25%)

- Sales momentum
- Recency weighting

Operational Risk (20%)

- Sales volatility
- Transaction volume

Customer Risk (15%)

- Customer concentration

Performance Risk (20%)

- Relative sales strength

Data Reliability Risk (20%)

- Outlier burden
- Data support quality

---

# Risk Interpretation

Score range:

```text
0 → Lowest relative concern
100 → Highest relative concern
```

The score is:

✅ Relative ranking metric

The score is NOT:

❌ Probability

Example:

```text
Risk Score = 60
```

Does NOT mean:

```text
60% chance of decline
```

Risk bands:

- Low = 0–24.9
- Moderate = 25–49.9
- High = 50–74.9
- Critical = 75–100

---

# Dashboard

Interactive dashboard includes:

### Executive KPIs

- Data quality score
- Issues detected
- Rows removed
- Highest-risk segment

### Risk Review

- Segment drilldown
- Risk drivers
- Composite risk chart
- Risk explanations

### Data Quality Review

- Missingness analysis
- Issue distribution
- Data preview

### Reporting

- Download cleaning report
- Download predictive output

Launch:

```bash
streamlit run dashboard.py
```

---

# Automated Testing

Current test coverage includes:

### Validation Tests

- Valid configuration
- Missing mappings
- Duplicate mappings

### Cleaning Tests

- Duplicate removal
- Invalid numeric detection

Run tests:

```bash
PYTHONPATH=. python3 -m pytest tests/
```

---

# Performance Benchmark

Cleaning pipeline benchmark results:

| Rows | Runtime |
|------|---------|
| 10,000 | 4.1 sec |
| 50,000 | 20.5 sec |
| 100,000 | 42.8 sec |

Benchmarks executed locally on macOS.

Current implementation handles 100k rows in under one minute.

---

# Project Structure

```text
retail-data-quality-risk-dashboard/

clean_retail_data.py
predictive_analytics.py
dashboard.py
validation.py
config.json
requirements.txt
README.md

sample_data/
└── demo_retail_dataset.csv

screenshots/
├── dashboard_overview.png
├── segment_analysis.png
└── data_quality.png

tests/
├── test_validation.py
├── test_cleaning.py
└── performance_test.py
```

---

# How To Run

Install:

```bash
pip install -r requirements.txt
```

Run cleaning:

```bash
python3 clean_retail_data.py
```

Run predictive model:

```bash
python3 predictive_analytics.py
```

Launch dashboard:

```bash
streamlit run dashboard.py
```

Run tests:

```bash
PYTHONPATH=. python3 -m pytest tests/
```

---

# Skills Demonstrated

Analytics:

- Data cleaning
- Missingness analysis
- Feature engineering
- Predictive analytics
- Explainable models
- Risk scoring

Technical:

- Python
- Pandas
- OpenPyXL
- Streamlit
- Plotly
- Pytest
- Validation pipelines

Business:

- Executive reporting
- Decision support
- Model transparency
- Risk interpretation
- Business communication

---

# Future Enhancements

Planned:

- Seasonality adjustment
- Rolling-window analysis
- Peer-relative scoring
- Basket behavior metrics
- Customer retention metrics
- Scenario simulation
- PDF export
- Multi-file uploads
- Larger dataset optimization

---

# Disclaimer

Created for portfolio and demonstration purposes.

Risk scores are intended for decision support and should not be interpreted as probabilities or guaranteed outcomes.