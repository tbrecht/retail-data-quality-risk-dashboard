import pandas as pd
import numpy as np
import time
from pathlib import Path
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from clean_retail_data import clean_and_report


def generate_dataset(rows):

    np.random.seed(42)

    df = pd.DataFrame({
        "Date": pd.date_range(
            "2025-01-01",
            periods=rows,
            freq="h"
        ),

        "Category": np.random.choice(
            [
                "Electronics",
                "Clothing",
                "Home",
                "Beauty"
            ],
            rows
        ),

        "Customer_ID": [
            f"C{i}"
            for i in range(rows)
        ],

        "Units_Sold": np.random.randint(
            1,
            20,
            rows
        ),

        "Unit_Price": np.random.randint(
            5,
            500,
            rows
        )
    })

    df["Total_Sales"] = (
        df["Units_Sold"] *
        df["Unit_Price"]
    )

    return df


sizes = [
    10000,
    50000,
    100000
]

results = []

for size in sizes:

    print(
        f"\nRunning benchmark: {size:,} rows"
    )

    df = generate_dataset(size)

    input_file = f"perf_{size}.csv"
    output_file = f"perf_{size}.xlsx"

    df.to_csv(
        input_file,
        index=False
    )

    start = time.time()

    clean_and_report(
        input_file,
        output_file
    )

    runtime = time.time() - start

    results.append({
        "rows": size,
        "runtime_seconds": runtime
    })

results_df = pd.DataFrame(results)

print("\nBenchmark Results")

print(results_df)