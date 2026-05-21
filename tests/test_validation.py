from validation import load_config
from pathlib import Path
import json
import tempfile


def test_valid_config():

    config = {
        "input_file": "sample_data/demo_retail_dataset.csv",
        "cleaning_output_file": "cleaning_report_output.xlsx",
        "predictive_output_file": "predictive_analytics_output.xlsx",
        "columns": {
            "sales": "Total_Sales",
            "category": "Category",
            "date": "Date",
            "customer": "Customer_ID"
        }
    }

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False
    ) as f:

        json.dump(config, f)

        path = f.name

    result = load_config(path)

    assert result["columns"]["sales"] == "Total_Sales"


def test_missing_sales_column():

    config = {
        "input_file": "sample_data/demo_retail_dataset.csv",
        "cleaning_output_file": "cleaning_report_output.xlsx",
        "predictive_output_file": "predictive_analytics_output.xlsx",
        "columns": {
            "category": "Category"
        }
    }

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False
    ) as f:

        json.dump(config, f)

        path = f.name

    try:
        load_config(path)

        assert False

    except ValueError:
        assert True


def test_duplicate_mapping():

    config = {
        "input_file": "sample_data/demo_retail_dataset.csv",
        "cleaning_output_file": "cleaning_report_output.xlsx",
        "predictive_output_file": "predictive_analytics_output.xlsx",
        "columns": {
            "sales": "Category",
            "category": "Category"
        }
    }

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False
    ) as f:

        json.dump(config, f)

        path = f.name

    try:
        load_config(path)

        assert False

    except ValueError:
        assert True