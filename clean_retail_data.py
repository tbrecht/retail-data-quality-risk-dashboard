import pandas as pd
import numpy as np
from openpyxl.utils import get_column_letter
from pathlib import Path
import re

INPUT_FILE = "retail_store_sales.csv"
OUTPUT_FILE = "cleaning_report_output.xlsx"
SHEET_NAME = None


def cell_ref(row_idx, col_idx):
    return f"{get_column_letter(col_idx + 1)}{row_idx + 2}"


def normalize_column_name(col):
    return re.sub(r"[^a-z0-9]+", "_", str(col).lower()).strip("_")


def infer_column_type(series):
    non_blank = series.dropna().astype(str).str.strip()
    non_blank = non_blank[non_blank != ""]

    if len(non_blank) == 0:
        return "unknown"

    numeric_parse = pd.to_numeric(non_blank, errors="coerce").notna().mean()
    date_parse = pd.to_datetime(non_blank, errors="coerce").notna().mean()

    if numeric_parse >= 0.80:
        return "numeric"
    if date_parse >= 0.80:
        return "date"
    return "text"


def is_identifier_column(col, series):
    col_name = normalize_column_name(col)
    values = series.dropna().astype(str).str.strip()
    values = values[values != ""]

    if len(values) == 0:
        return False

    unique_ratio = values.nunique(dropna=True) / len(values)

    id_patterns = [
        r"(^|_)id($|_)",
        r"customer_id",
        r"client_id",
        r"user_id",
        r"order_id",
        r"transaction_id",
        r"record_id",
        r"product_id",
        r"employee_id",
        r"account_id",
        r"invoice_id",
        r"sku",
        r"key",
        r"number",
        r"code"
    ]

    if any(re.search(pattern, col_name) for pattern in id_patterns):
        return True

    if unique_ratio >= 0.90:
        return True

    return False


def is_human_readable_distribution_column(col, series):
    col_name = normalize_column_name(col)
    values = series.dropna().astype(str).str.strip()
    values = values[values != ""]

    if len(values) == 0:
        return False

    unique_count = values.nunique(dropna=True)
    total_count = len(values)
    unique_ratio = unique_count / total_count

    excluded_keywords = [
        "id",
        "item",
        "sku",
        "code",
        "key",
        "number",
        "transaction",
        "invoice",
        "record"
    ]

    if any(keyword in col_name for keyword in excluded_keywords):
        return False

    if unique_ratio >= 0.50:
        return False

    if unique_count > 50:
        return False

    avg_length = values.str.len().mean()

    if avg_length <= 2:
        return False

    return True


def create_missingness_report(original_df, cleaned_df):
    rows = []

    for col in original_df.columns:
        original_missing = original_df[col].isna().sum()
        original_percent = (original_missing / len(original_df)) * 100

        if col in cleaned_df.columns and len(cleaned_df) > 0:
            cleaned_missing = cleaned_df[col].isna().sum()
            cleaned_percent = (cleaned_missing / len(cleaned_df)) * 100
        else:
            cleaned_missing = None
            cleaned_percent = None

        rows.append({
            "column": col,
            "original_missing_count": original_missing,
            "original_total_rows": len(original_df),
            "original_missing_percent": f"{original_percent:.2f}%",
            "cleaned_missing_count": cleaned_missing,
            "cleaned_total_rows": len(cleaned_df),
            "cleaned_missing_percent": (
                f"{cleaned_percent:.2f}%" if cleaned_percent is not None else None
            ),
            "missingness_flag": (
                "High Missingness" if original_percent >= 10 else
                "Moderate Missingness" if original_percent >= 5 else
                "Low Missingness"
            )
        })

    return pd.DataFrame(rows)


def clean_and_report(input_file, output_file, sheet_name=None):
    input_path = Path(input_file)

    if input_path.suffix.lower() in [".xlsx", ".xls"]:
        raw_df = pd.read_excel(input_file, sheet_name=sheet_name or 0, dtype=object)
        source_sheet = sheet_name or pd.ExcelFile(input_file).sheet_names[0]
    elif input_path.suffix.lower() == ".csv":
        raw_df = pd.read_csv(input_file, dtype=object)
        source_sheet = "csv_input"
    else:
        raise ValueError("Input must be .xlsx, .xls, or .csv")

    original_df = raw_df.copy()
    clean_df = raw_df.copy()

    change_log = []
    rows_to_remove = set()

    empty_rows = clean_df[clean_df.isna().all(axis=1)].index.tolist()
    for r in empty_rows:
        change_log.append({
            "sheet": source_sheet,
            "cell": f"Row {r + 2}",
            "row_number": r + 2,
            "column": "ALL",
            "error_type": "Fully empty row",
            "original_value": "",
            "action_taken": "Removed from cleaned dataset",
            "reason": "Row contains no usable data"
        })
        rows_to_remove.add(r)

    duplicate_mask = clean_df.duplicated(keep="first")
    duplicate_rows = clean_df[duplicate_mask].index.tolist()

    for r in duplicate_rows:
        change_log.append({
            "sheet": source_sheet,
            "cell": f"Row {r + 2}",
            "row_number": r + 2,
            "column": "ALL",
            "error_type": "Duplicate row",
            "original_value": "Entire row duplicated",
            "action_taken": "Removed from cleaned dataset",
            "reason": "Duplicate record found"
        })
        rows_to_remove.add(r)

    expected_types = {
        col: infer_column_type(clean_df[col])
        for col in clean_df.columns
    }

    identifier_columns = {
        col for col in clean_df.columns
        if is_identifier_column(col, clean_df[col])
    }

    for col_idx, col in enumerate(clean_df.columns):
        expected = expected_types[col]

        for row_idx, value in clean_df[col].items():
            if row_idx in rows_to_remove:
                continue

            if pd.isna(value) or str(value).strip() == "":
                continue

            value_str = str(value).strip()
            excel_cell = cell_ref(row_idx, col_idx)

            if expected == "numeric":
                parsed = pd.to_numeric(value_str, errors="coerce")

                if pd.isna(parsed):
                    change_log.append({
                        "sheet": source_sheet,
                        "cell": excel_cell,
                        "row_number": row_idx + 2,
                        "column": col,
                        "error_type": "Text found where numeric expected",
                        "original_value": value,
                        "action_taken": "Row removed from cleaned dataset",
                        "reason": "Could not safely convert value to numeric"
                    })
                    rows_to_remove.add(row_idx)
                else:
                    clean_df.at[row_idx, col] = parsed

            elif expected == "date":
                parsed = pd.to_datetime(value_str, errors="coerce")

                if pd.isna(parsed):
                    change_log.append({
                        "sheet": source_sheet,
                        "cell": excel_cell,
                        "row_number": row_idx + 2,
                        "column": col,
                        "error_type": "Invalid date value",
                        "original_value": value,
                        "action_taken": "Row removed from cleaned dataset",
                        "reason": "Could not safely convert value to date"
                    })
                    rows_to_remove.add(row_idx)
                else:
                    clean_df.at[row_idx, col] = parsed

            elif expected == "text":
                if col in identifier_columns:
                    clean_df.at[row_idx, col] = value_str
                    continue

                numeric_check = pd.to_numeric(value_str, errors="coerce")

                if not pd.isna(numeric_check):
                    change_log.append({
                        "sheet": source_sheet,
                        "cell": excel_cell,
                        "row_number": row_idx + 2,
                        "column": col,
                        "error_type": "Numeric found where text expected",
                        "original_value": value,
                        "action_taken": "Row removed from cleaned dataset",
                        "reason": "Column appears to contain categorical/text values"
                    })
                    rows_to_remove.add(row_idx)
                else:
                    cleaned_text = value_str.strip()

                    if cleaned_text != value:
                        change_log.append({
                            "sheet": source_sheet,
                            "cell": excel_cell,
                            "row_number": row_idx + 2,
                            "column": col,
                            "error_type": "Text formatting issue",
                            "original_value": value,
                            "action_taken": cleaned_text,
                            "reason": "Trimmed leading/trailing whitespace"
                        })

                    clean_df.at[row_idx, col] = cleaned_text

    cleaned_df = clean_df.drop(index=list(rows_to_remove)).reset_index(drop=True)

    numeric_summary = []

    for col, expected in expected_types.items():
        if expected == "numeric" and col in cleaned_df.columns:
            values = pd.to_numeric(cleaned_df[col], errors="coerce").dropna()

            if len(values) > 0:
                numeric_summary.append({
                    "column": col,
                    "mean": values.mean(),
                    "sd": values.std(),
                    "median": values.median(),
                    "q1": values.quantile(0.25),
                    "q3": values.quantile(0.75),
                    "n": len(values)
                })

    numeric_summary_df = pd.DataFrame(numeric_summary)

    text_dist_rows = []

    for col, expected in expected_types.items():
        if expected != "text" or col not in cleaned_df.columns:
            continue

        if col in identifier_columns:
            continue

        if not is_human_readable_distribution_column(col, cleaned_df[col]):
            continue

        values = cleaned_df[col].fillna("Missing").astype(str).str.strip()
        total_count_for_column = len(values)
        counts = values.value_counts(dropna=False)

        text_dist_rows.append({
            "column": f"--- {col} ---",
            "value": "",
            "count_within_column": "",
            "total_rows_for_column": "",
            "percent_within_column": ""
        })

        for value, count in counts.items():
            text_dist_rows.append({
                "column": col,
                "value": value,
                "count_within_column": count,
                "total_rows_for_column": total_count_for_column,
                "percent_within_column": f"{((count / total_count_for_column) * 100):.2f}%"
            })

        text_dist_rows.append({
            "column": col,
            "value": "TOTAL",
            "count_within_column": total_count_for_column,
            "total_rows_for_column": total_count_for_column,
            "percent_within_column": "100.00%"
        })

        text_dist_rows.append({
            "column": "",
            "value": "",
            "count_within_column": "",
            "total_rows_for_column": "",
            "percent_within_column": ""
        })

    text_distribution_df = pd.DataFrame(text_dist_rows)
    change_log_df = pd.DataFrame(change_log)
    missingness_df = create_missingness_report(original_df, cleaned_df)

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        original_df.to_excel(writer, sheet_name="Original_Data", index=False)
        cleaned_df.to_excel(writer, sheet_name="Cleaned_Data", index=False)
        change_log_df.to_excel(writer, sheet_name="Change_Log", index=False)
        missingness_df.to_excel(writer, sheet_name="Missingness", index=False)
        numeric_summary_df.to_excel(writer, sheet_name="Numeric_Summary", index=False)
        text_distribution_df.to_excel(writer, sheet_name="Text_Distributions", index=False)

    print(f"Done. Output saved to: {output_file}")
    print(f"Original rows: {len(original_df)}")
    print(f"Cleaned rows: {len(cleaned_df)}")
    print(f"Rows removed: {len(rows_to_remove)}")
    print(f"Changes/errors logged: {len(change_log_df)}")


if __name__ == "__main__":
    clean_and_report(INPUT_FILE, OUTPUT_FILE, SHEET_NAME)