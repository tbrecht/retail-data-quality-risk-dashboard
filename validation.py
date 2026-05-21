import json
from pathlib import Path


def load_config(config_path="config.json"):

    if not Path(config_path).exists():
        raise FileNotFoundError(
            "config.json not found. Create config.json before running."
        )

    with open(config_path, "r") as f:
        config = json.load(f)

    required_top = [
        "input_file",
        "cleaning_output_file",
        "predictive_output_file",
        "columns"
    ]

    missing = [
        x for x in required_top
        if x not in config
    ]

    if missing:
        raise ValueError(
            f"Missing config fields: {missing}"
        )

    required_columns = [
        "sales",
        "category"
    ]

    missing_columns = [
        x for x in required_columns
        if x not in config["columns"]
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required column mappings: {missing_columns}"
        )

    input_file = Path(config["input_file"])

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_file}"
        )

    valid_suffixes = [
        ".csv",
        ".xlsx",
        ".xls"
    ]

    if input_file.suffix.lower() not in valid_suffixes:
        raise ValueError(
            "Supported input formats: .csv .xlsx .xls"
        )

    mapped_columns = list(
        config["columns"].values()
    )

    duplicates = {
        x for x in mapped_columns
        if mapped_columns.count(x) > 1
    }

    if duplicates:
        raise ValueError(
            f"Duplicate column mappings detected: {duplicates}"
        )

    return config