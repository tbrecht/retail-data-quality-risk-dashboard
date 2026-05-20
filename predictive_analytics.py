import pandas as pd
import numpy as np
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment
from openpyxl.chart import BarChart, Reference

INPUT_FILE = "cleaning_report_output.xlsx"
OUTPUT_FILE = "predictive_analytics_output.xlsx"
SHEET_NAME = "Cleaned_Data"


def find_column(df, keywords):
    for col in df.columns:
        col_clean = str(col).lower().replace(" ", "_")
        if any(k in col_clean for k in keywords):
            return col
    return None


def normalize_score(series):
    if series.max() == series.min():
        return pd.Series([0] * len(series), index=series.index)
    return ((series - series.min()) / (series.max() - series.min())) * 100


def risk_level(score):
    if score >= 75:
        return "Critical"
    if score >= 50:
        return "High"
    if score >= 25:
        return "Moderate"
    return "Low"


def apply_formatting_and_charts(output_file):
    wb = load_workbook(output_file)

    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                cell.font = Font(size=14)
                cell.alignment = Alignment(wrap_text=True, vertical="top")

        for col in ws.columns:
            max_length = 0
            col_letter = col[0].column_letter

            for cell in col:
                if cell.value is not None:
                    max_length = max(max_length, len(str(cell.value)))

            ws.column_dimensions[col_letter].width = min(max_length + 4, 65)

    if "Model_Insights" in wb.sheetnames:
        ws = wb["Model_Insights"]

        chart = BarChart()
        chart.title = "Top Segment Risk Scores"
        chart.y_axis.title = "Risk Score"
        chart.x_axis.title = "Segment"

        data = Reference(ws, min_col=2, min_row=1, max_row=min(ws.max_row, 11))
        cats = Reference(ws, min_col=1, min_row=2, max_row=min(ws.max_row, 11))

        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        chart.height = 12
        chart.width = 24

        # Place chart far enough right so it does not overlap text columns
        ws.add_chart(chart, "H2")

    wb.save(output_file)


def run_predictive_analysis():
    if not Path(INPUT_FILE).exists():
        raise FileNotFoundError(f"{INPUT_FILE} not found.")

    df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME)

    sales_col = find_column(df, ["sales", "amount", "revenue", "price", "total"])
    category_col = find_column(df, ["category", "product", "region", "segment"])
    date_col = find_column(df, ["date", "time"])

    if sales_col is None:
        raise ValueError("Could not identify a sales/revenue column.")

    if category_col is None:
        raise ValueError("Could not identify a category/product/region column.")

    df[sales_col] = pd.to_numeric(df[sales_col], errors="coerce")
    df = df.dropna(subset=[sales_col, category_col])

    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=[date_col])

    grouped = df.groupby(category_col)[sales_col].agg(
        total_sales="sum",
        average_sale="mean",
        sales_sd="std",
        transaction_count="count"
    ).reset_index()

    grouped["sales_sd"] = grouped["sales_sd"].fillna(0)

    grouped["sales_volatility"] = (
        grouped["sales_sd"] / grouped["average_sale"]
    ).replace([np.inf, -np.inf], 0).fillna(0)

    grouped["sales_share"] = grouped["total_sales"] / grouped["total_sales"].sum()

    if date_col:
        df = df.sort_values(date_col)
        midpoint = df[date_col].median()

        early = (
            df[df[date_col] <= midpoint]
            .groupby(category_col)[sales_col]
            .sum()
            .reset_index(name="early_sales")
        )

        recent = (
            df[df[date_col] > midpoint]
            .groupby(category_col)[sales_col]
            .sum()
            .reset_index(name="recent_sales")
        )

        grouped = grouped.merge(early, on=category_col, how="left")
        grouped = grouped.merge(recent, on=category_col, how="left")

        grouped["early_sales"] = grouped["early_sales"].fillna(0)
        grouped["recent_sales"] = grouped["recent_sales"].fillna(0)

        grouped["sales_momentum"] = (
            (grouped["recent_sales"] - grouped["early_sales"]) /
            grouped["early_sales"].replace(0, np.nan)
        ).replace([np.inf, -np.inf], np.nan).fillna(0)

    else:
        grouped["early_sales"] = np.nan
        grouped["recent_sales"] = np.nan
        grouped["sales_momentum"] = 0

    grouped["low_sales_score"] = 100 - normalize_score(grouped["total_sales"])
    grouped["volatility_score"] = normalize_score(grouped["sales_volatility"])
    grouped["decline_score"] = normalize_score(-grouped["sales_momentum"])
    grouped["low_volume_score"] = 100 - normalize_score(grouped["transaction_count"])

    grouped["composite_risk_score"] = (
        0.35 * grouped["decline_score"] +
        0.25 * grouped["volatility_score"] +
        0.25 * grouped["low_sales_score"] +
        0.15 * grouped["low_volume_score"]
    ).round(1)

    grouped["risk_level"] = grouped["composite_risk_score"].apply(risk_level)

    grouped = grouped.sort_values("composite_risk_score", ascending=False)

    model_insights = grouped[
        [
            category_col,
            "composite_risk_score",
            "risk_level",
            "total_sales",
            "sales_momentum",
            "sales_volatility"
        ]
    ].head(10).copy()

    model_insights["nontechnical_interpretation"] = model_insights.apply(
        lambda row: (
            f"{row[category_col]} is classified as {row['risk_level']} risk "
            f"with a risk score of {row['composite_risk_score']}. "
            f"This is a relative ranking score, not a probability. "
            f"For example, a score of 60 does not mean there is a 60% chance of failure. "
            f"It means this segment scored higher than lower-risk segments based on the risk factors used in the model."
        ),
        axis=1
    )

    risk_explainer = pd.DataFrame({
        "section": [
            "What the risk score means",
            "What the risk score does NOT mean",
            "Score range",
            "Low risk cutoff",
            "Moderate risk cutoff",
            "High risk cutoff",
            "Critical risk cutoff",
            "Risk score formula",
            "Decline score",
            "Volatility score",
            "Low sales score",
            "Low volume score"
        ],
        "explanation": [
            "The composite risk score is a relative business risk ranking from 0 to 100. Higher scores indicate that a segment should receive more attention.",
            "The score is not a probability. A score of 60 does not mean there is a 60% chance that the segment will fail or decline.",
            "Scores range from 0 to 100, where 0 indicates the lowest relative concern and 100 indicates the highest relative concern within this dataset.",
            "0 to 24.9 = Low risk",
            "25 to 49.9 = Moderate risk",
            "50 to 74.9 = High risk",
            "75 to 100 = Critical risk",
            "Composite Risk Score = 35% decline score + 25% volatility score + 25% low-sales score + 15% low-volume score.",
            "Measures whether recent sales are weaker compared with earlier sales periods.",
            "Measures how unstable or inconsistent sales are for the segment.",
            "Measures whether the segment has relatively weak total sales compared with other segments.",
            "Measures whether the segment has relatively low transaction volume compared with other segments."
        ]
    })

    executive_summary = pd.DataFrame({
        "section": [
            "Purpose",
            "Main result",
            "Risk score reminder",
            "Recommended action"
        ],
        "summary": [
            "This analysis identifies which business segments appear most at risk of future underperformance.",
            f"The highest-risk segment is {grouped.iloc[0][category_col]} with a risk score of {grouped.iloc[0]['composite_risk_score']} ({grouped.iloc[0]['risk_level']} risk).",
            "The risk score is a relative ranking score, not a probability. A score of 60 does not mean a 60% chance of decline.",
            "Review High and Critical risk segments first. These may require pricing review, marketing support, inventory review, or deeper operational investigation."
        ]
    })

    scientific_breakdown = pd.DataFrame({
        "topic": [
            "Model type",
            "Business objective",
            "Unit of analysis",
            "Outcome being estimated",
            "Features engineered",
            "Composite score formula",
            "Risk score interpretation",
            "Risk score cutoffs",
            "Why this approach was used",
            "Model limitations",
            "Data limitations",
            "Recommended next step"
        ],
        "details": [
            "Transparent composite risk scoring model using engineered sales-performance features.",
            "Identify segments that may be at risk of future underperformance.",
            f"Each row in the model output represents one value of the '{category_col}' column.",
            "The model estimates relative business risk, not a guaranteed future outcome.",
            "Total sales, average sale, transaction count, sales volatility, sales share, sales momentum, low-sales score, volatility score, decline score, and low-volume score.",
            "Composite Risk Score = 35% decline score + 25% volatility score + 25% low-sales score + 15% low-volume score.",
            "The risk score is a relative ranking from 0 to 100. It is not a probability and should not be interpreted as percent likelihood of decline.",
            "Low: 0-24.9; Moderate: 25-49.9; High: 50-74.9; Critical: 75-100.",
            "A transparent scoring model was chosen because it is easier for nontechnical stakeholders to understand and audit than a black-box model.",
            "This is not a causal model. It does not prove why performance changed. It ranks segments by relative risk based on observed sales patterns.",
            "Results depend on the quality, completeness, and time coverage of the cleaned dataset. If dates, categories, or sales fields are incomplete or inconsistent, model reliability may decrease.",
            "Use this model as an early warning system, then investigate high-risk segments with additional business context."
        ]
    })

    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        executive_summary.to_excel(writer, sheet_name="Executive_Summary", index=False)
        model_insights.to_excel(writer, sheet_name="Model_Insights", index=False)
        risk_explainer.to_excel(writer, sheet_name="Risk_Score_Explainer", index=False)
        scientific_breakdown.to_excel(writer, sheet_name="Scientific_Breakdown", index=False)
        grouped.to_excel(writer, sheet_name="Risk_Model_Output", index=False)

    apply_formatting_and_charts(OUTPUT_FILE)

    print("\nPredictive analytics complete.")
    print(f"Output saved to: {OUTPUT_FILE}")
    print("\nNontechnical summary:")
    print(
        f"The highest-risk segment is {grouped.iloc[0][category_col]} "
        f"with a score of {grouped.iloc[0]['composite_risk_score']} "
        f"({grouped.iloc[0]['risk_level']} risk)."
    )
    print("Reminder: the risk score is a relative ranking, not a probability.")


if __name__ == "__main__":
    run_predictive_analysis()