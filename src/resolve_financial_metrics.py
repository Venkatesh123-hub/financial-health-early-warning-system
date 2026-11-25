
from pathlib import Path

import pandas as pd

from financial_metrics import FINANCIAL_METRICS

# Project directories
BASE_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DATA_DIR = (
    BASE_DIR / "data" / "processed"
)

INPUT_FILE = (
    PROCESSED_DATA_DIR
    / "annual_financial_data_preliminary.csv"
)

OUTPUT_FILE = (
    PROCESSED_DATA_DIR
    / "annual_financial_data_transformed.csv"
)

LOG_FILE = (
    PROCESSED_DATA_DIR
    / "financial_transformation_log.csv"
)

# Load preliminary financial dataset
df = pd.read_csv(INPUT_FILE)

transformation_log = []


def calculate_metric(index, metric, components, operation):

    # Preserve existing reported values
    if pd.notna(df.at[index, metric]):
        return

    values = [
        df.at[index, component]
        for component in components
    ]

    # Never calculate using missing components
    if any(pd.isna(value) for value in values):
        return

    if operation == "subtract":
        result = values[0] - values[1]

    elif operation == "add":
        result = sum(values)

    else:
        raise ValueError("Unsupported operation")

    df.at[index, metric] = result

    transformation_log.append({
        "ticker": df.at[index, "ticker"],
        "fiscal_year": df.at[index, "fiscal_year"],
        "metric": metric,
        "method": "Calculated",
        "components": " | ".join(components),
        "operation": operation,
        "value": result
    })


# Initialize calculated metric
df["free_cash_flow"] = float("nan")

# Apply financial calculations
for index in df.index:

    # Gross profit
    calculate_metric(
        index,
        "gross_profit",
        ["revenue", "cost_of_revenue"],
        "subtract"
    )

    # Operating expenses
    calculate_metric(
        index,
        "operating_expenses",
        ["gross_profit", "operating_income"],
        "subtract"
    )

    # Preliminary short-term debt calculation
    # Pending annual report reconciliation
    calculate_metric(
        index,
        "short_term_debt",
        [
            "commercial_paper",
            "current_long_term_debt"
        ],
        "add"
    )

    # Free cash flow
    calculate_metric(
        index,
        "free_cash_flow",
        [
            "operating_cash_flow",
            "capital_expenditure"
        ],
        "subtract"
    )

# Target financial metrics
target_metrics = [
    *FINANCIAL_METRICS.keys(),
    "free_cash_flow"
]

# Save transformed dataset
df.to_csv(OUTPUT_FILE, index=False)

# Save transformation audit log
log_df = pd.DataFrame(transformation_log)

log_df.to_csv(LOG_FILE, index=False)

# Summary
print("\n" + "=" * 70)
print("FINANCIAL TRANSFORMATION SUMMARY")
print("=" * 70)

print(f"Companies: {df['ticker'].nunique()}")
print(f"Financial records: {len(df)}")
print(f"Target financial metrics: {len(target_metrics)}")

print(
    f"Calculated values: "
    f"{len(transformation_log)}"
)

print("\nCalculations by metric:")

print(
    log_df["metric"].value_counts().to_string()
)

total_values = len(df) * len(target_metrics)

missing_values = int(
    df[target_metrics].isna().sum().sum()
)

available_values = total_values - missing_values

completeness = (
    available_values / total_values
) * 100

print(f"\nTotal target values: {total_values}")
print(f"Available target values: {available_values}")
print(f"Missing target values: {missing_values}")
print(f"Data completeness: {completeness:.2f}%")

# Display unresolved target values
print("\nUNRESOLVED FINANCIAL VALUES")

for index in df.index:

    for metric in target_metrics:

        if pd.isna(df.at[index, metric]):

            print(
                f"{df.at[index, 'ticker']} | "
                f"{df.at[index, 'fiscal_year']} | "
                f"{metric}"
            )

print(f"\nTransformed dataset: {OUTPUT_FILE}")
print(f"Transformation log: {LOG_FILE}")

print("\nFinancial transformation completed.")
