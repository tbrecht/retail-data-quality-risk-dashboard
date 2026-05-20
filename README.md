# Retail Data Quality & Predictive Analytics Dashboard

End-to-end analytics workflow built in Python for cleaning retail data, documenting data quality issues, generating predictive insights, and presenting results in an interactive dashboard.

## Features

### Data Cleaning
- Preserves original dataset
- Creates cleaned output
- Detects duplicates
- Removes unusable rows
- Logs exact error locations
- Missingness reporting
- Numeric summaries
- Human-readable text distributions

### Predictive Analytics
- Composite risk scoring model
- Sales momentum analysis
- Volatility assessment
- Transaction volume scoring
- Business-friendly interpretation
- Scientific methodology documentation

### Dashboard
Interactive Streamlit interface including:

- Data quality score
- Risk visualizations
- Segment drilldown
- Business recommendations
- Downloadable outputs

---

## Files

### clean_retail_data.py

Performs data cleaning and generates:

- Original_Data
- Cleaned_Data
- Change_Log
- Missingness
- Numeric_Summary
- Text_Distributions

---

### predictive_analytics.py

Builds risk model output:

- Executive summary
- Model insights
- Risk score explanation
- Scientific breakdown
- Risk model output

---

### dashboard.py

Interactive Streamlit application for reviewing results.

Run:

```bash
streamlit run dashboard.py