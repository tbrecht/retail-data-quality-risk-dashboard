import pandas as pd
from pathlib import Path
import tempfile
from clean_retail_data import clean_and_report


def test_duplicate_removal():

    df = pd.DataFrame({
        "Date": [
            "2025-01-01",
            "2025-01-01"
        ],
        "Category": [
            "Electronics",
            "Electronics"
        ],
        "Customer_ID": [
            "C001",
            "C001"
        ],
        "Units_Sold": [
            2,
            2
        ],
        "Unit_Price": [
            100,
            100
        ],
        "Total_Sales": [
            200,
            200
        ]
    })

    with tempfile.TemporaryDirectory() as tmp:

        input_path = Path(tmp) / "test.csv"
        output_path = Path(tmp) / "out.xlsx"

        df.to_csv(
            input_path,
            index=False
        )

        clean_and_report(
            str(input_path),
            str(output_path)
        )

        cleaned = pd.read_excel(
            output_path,
            sheet_name="Cleaned_Data"
        )

        assert len(cleaned) == 1


def test_invalid_numeric_removed():

    df = pd.DataFrame({
        "Date": [
            "2025-01-01",
            "2025-01-02"
        ],
        "Category": [
            "Electronics",
            "Electronics"
        ],
        "Customer_ID": [
            "C001",
            "C002"
        ],
        "Units_Sold": [
            "abc",
            2
        ],
        "Unit_Price": [
            100,
            100
        ],
        "Total_Sales": [
            100,
            200
        ]
    })

    with tempfile.TemporaryDirectory() as tmp:

        input_path = Path(tmp) / "bad.csv"
        output_path = Path(tmp) / "bad_out.xlsx"

        df.to_csv(
            input_path,
            index=False
        )

        clean_and_report(
            str(input_path),
            str(output_path)
        )

        cleaned = pd.read_excel(
            output_path,
            sheet_name="Cleaned_Data"
        )

        assert len(cleaned) == 1