import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

CLEANING_FILE = "cleaning_report_output.xlsx"
PREDICTIVE_FILE = "predictive_analytics_output.xlsx"

st.set_page_config(
    page_title="Retail Analytics Dashboard",
    layout="wide"
)

st.title("Retail Analytics Command Center")
st.caption("Interactive summary of data quality, risk scoring, and business performance.")

if not Path(CLEANING_FILE).exists() or not Path(PREDICTIVE_FILE).exists():
    st.error("Required output files not found. Run the cleaning and predictive analytics scripts first.")
    st.stop()

original_df = pd.read_excel(CLEANING_FILE, sheet_name="Original_Data")
cleaned_df = pd.read_excel(CLEANING_FILE, sheet_name="Cleaned_Data")
change_log = pd.read_excel(CLEANING_FILE, sheet_name="Change_Log")
missingness = pd.read_excel(CLEANING_FILE, sheet_name="Missingness")

executive_summary = pd.read_excel(PREDICTIVE_FILE, sheet_name="Executive_Summary")
model_insights = pd.read_excel(PREDICTIVE_FILE, sheet_name="Model_Insights")
risk_explainer = pd.read_excel(PREDICTIVE_FILE, sheet_name="Risk_Score_Explainer")
risk_model = pd.read_excel(PREDICTIVE_FILE, sheet_name="Risk_Model_Output")

segment_col = risk_model.columns[0]

records_removed = len(original_df) - len(cleaned_df)
issues_found = len(change_log)

missingness["original_missing_percent_num"] = (
    missingness["original_missing_percent"]
    .astype(str)
    .str.replace("%", "", regex=False)
    .astype(float)
)

avg_missingness = missingness["original_missing_percent_num"].mean()
data_quality_score = max(0, 100 - avg_missingness)

highest_risk = risk_model.sort_values("composite_risk_score", ascending=False).iloc[0]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Data Quality Score", f"{data_quality_score:.1f}/100")
col2.metric("Issues Found", f"{issues_found:,}")
col3.metric("Rows Removed", f"{records_removed:,}")
col4.metric("Highest Risk Segment", str(highest_risk[segment_col]))

st.divider()

left, right = st.columns([1.2, 1])

with left:
    st.subheader("Top Risk Segments")

    top_risk = (
        risk_model
        .sort_values("composite_risk_score", ascending=False)
        .head(10)
    )

    fig = px.bar(
        top_risk,
        x=segment_col,
        y="composite_risk_score",
        color="risk_level",
        title="Composite Risk Score by Segment",
        labels={
            segment_col: "Segment",
            "composite_risk_score": "Risk Score",
            "risk_level": "Risk Level"
        }
    )

    fig.update_layout(
        height=450,
        xaxis_tickangle=-35,
        margin=dict(l=20, r=20, t=60, b=120)
    )

    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Risk Score Reminder")

    st.info(
        "The risk score is a relative ranking from 0 to 100. "
        "It is not a probability. A score of 60 does not mean a 60% chance of decline."
    )

    st.markdown(
        """
        **Risk bands**

        Low: 0–24.9  
        Moderate: 25–49.9  
        High: 50–74.9  
        Critical: 75–100
        """
    )

st.divider()

st.subheader("Explore a Segment")

segment_options = risk_model[segment_col].dropna().astype(str).tolist()
selected_segment = st.selectbox("Choose a segment to review:", segment_options)

segment_row = risk_model[risk_model[segment_col].astype(str) == selected_segment].iloc[0]

s1, s2, s3, s4 = st.columns(4)

s1.metric("Risk Score", segment_row["composite_risk_score"])
s2.metric("Risk Level", segment_row["risk_level"])
s3.metric("Total Sales", f"{segment_row['total_sales']:,.2f}")
s4.metric("Transactions", f"{int(segment_row['transaction_count']):,}")

st.markdown("### Why this segment was flagged")

explanation = (
    f"**{selected_segment}** is classified as **{segment_row['risk_level']} risk** "
    f"with a score of **{segment_row['composite_risk_score']}**. "
    f"This score is based on sales momentum, volatility, total sales strength, "
    f"and transaction volume."
)

st.write(explanation)

risk_components = pd.DataFrame({
    "Component": [
        "Decline Score",
        "Volatility Score",
        "Low Sales Score",
        "Low Volume Score"
    ],
    "Score": [
        segment_row["decline_score"],
        segment_row["volatility_score"],
        segment_row["low_sales_score"],
        segment_row["low_volume_score"]
    ]
})

fig_components = px.bar(
    risk_components,
    x="Component",
    y="Score",
    title=f"Risk Drivers for {selected_segment}",
    labels={"Score": "Component Score"}
)

fig_components.update_layout(height=400)

st.plotly_chart(fig_components, use_container_width=True)

st.divider()

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Data Issues by Type")

    if not change_log.empty:
        issue_counts = change_log["error_type"].value_counts().reset_index()
        issue_counts.columns = ["Issue Type", "Count"]

        fig_issues = px.bar(
            issue_counts,
            x="Issue Type",
            y="Count",
            title="Detected Data Issues"
        )

        fig_issues.update_layout(
            height=400,
            xaxis_tickangle=-30,
            margin=dict(l=20, r=20, t=60, b=100)
        )

        st.plotly_chart(fig_issues, use_container_width=True)
    else:
        st.success("No data quality issues were logged.")

with col_b:
    st.subheader("Missingness by Column")

    fig_missing = px.bar(
        missingness.sort_values("original_missing_percent_num", ascending=False),
        x="column",
        y="original_missing_percent_num",
        title="Missing Data Percentage",
        labels={
            "column": "Column",
            "original_missing_percent_num": "Missing %"
        }
    )

    fig_missing.update_layout(
        height=400,
        xaxis_tickangle=-30,
        margin=dict(l=20, r=20, t=60, b=100)
    )

    st.plotly_chart(fig_missing, use_container_width=True)

st.divider()

st.subheader("Recommended Next Actions")

if segment_row["risk_level"] in ["Critical", "High"]:
    st.warning(
        f"{selected_segment} should be reviewed soon. Focus on recent performance trends, "
        f"sales volatility, and whether low transaction volume is driving the risk score."
    )
elif segment_row["risk_level"] == "Moderate":
    st.info(
        f"{selected_segment} does not appear urgent, but it should be monitored. "
        f"Look for early signs of weakening sales momentum or increasing volatility."
    )
else:
    st.success(
        f"{selected_segment} appears relatively stable based on this dataset. "
        f"Continue monitoring, but it is not currently a priority risk area."
    )

with st.expander("Show model explanation"):
    for _, row in risk_explainer.iterrows():
        st.markdown(f"**{row['section']}**")
        st.write(row["explanation"])

with st.expander("Preview cleaned data"):
    st.dataframe(cleaned_df.head(100), use_container_width=True)

st.divider()

st.subheader("Download Reports")

d1, d2 = st.columns(2)

with d1:
    with open(CLEANING_FILE, "rb") as f:
        st.download_button(
            "Download Cleaning Report",
            data=f,
            file_name=CLEANING_FILE,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

with d2:
    with open(PREDICTIVE_FILE, "rb") as f:
        st.download_button(
            "Download Predictive Analytics Report",
            data=f,
            file_name=PREDICTIVE_FILE,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )