
from pathlib import Path

import numpy as np
import pandas as pd

from financial_metrics import (
    FINANCIAL_METRICS,
    COMPANIES,
    START_YEAR,
    END_YEAR,
    FISCAL_YEAR_ENDS,
    CURRENCY
)

# ==================================================
# PROJECT CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = (
    PROCESSED_DIR
    / "annual_financial_data_reconciled.csv"
)

OUTPUT_FILE = (
    PROCESSED_DIR
    / "financial_validation_report.csv"
)

AUDIT_FILE = (
    PROCESSED_DIR
    / "debt_reconciliation_log.csv"
)

TOLERANCE = 1_000_000

df = pd.read_csv(INPUT_FILE)

validation_results = []

target_metrics = [
    *FINANCIAL_METRICS.keys(),
    "free_cash_flow"
]

# ==================================================
# VALIDATION FUNCTION
# ==================================================

def record_validation(
    check,
    passed,
    details,
    ticker="ALL",
    year="ALL",
    warning=False
):

    if passed:
        status = "PASS"
    elif warning:
        status = "WARNING"
    else:
        status = "FAIL"

    validation_results.append({
        "ticker": ticker,
        "fiscal_year": year,
        "validation_check": check,
        "status": status,
        "details": details
    })


# ==================================================
# DATASET-LEVEL VALIDATION
# ==================================================

print("=" * 70)
print("FINANCIAL DATA VALIDATION ENGINE")
print("=" * 70)

expected_years = set(
    range(START_YEAR, END_YEAR + 1)
)

expected_records = (
    len(COMPANIES) * len(expected_years)
)

# 1. Record count

record_validation(
    "Record Count",
    len(df) == expected_records,
    f"Expected: {expected_records}, Actual: {len(df)}"
)

# 2. Duplicate records

duplicates = int(
    df.duplicated(
        subset=["ticker", "fiscal_year"]
    ).sum()
)

record_validation(
    "Duplicate Records",
    duplicates == 0,
    f"Duplicate records: {duplicates}"
)

# 3. Missing values

missing_values = int(
    df[target_metrics].isna().sum().sum()
)

record_validation(
    "Missing Financial Values",
    missing_values == 0,
    f"Missing values: {missing_values}"
)

# 4. Company coverage

actual_companies = set(df["ticker"])

record_validation(
    "Company Coverage",
    actual_companies == set(COMPANIES),
    f"Companies: {sorted(actual_companies)}"
)

# 5. Fiscal year coverage

for ticker in COMPANIES:

    actual_years = set(
        df.loc[
            df["ticker"] == ticker,
            "fiscal_year"
        ]
    )

    record_validation(
        "Fiscal Year Coverage",
        actual_years == expected_years,
        f"Years: {sorted(actual_years)}",
        ticker=ticker
    )

# 6. Currency validation

record_validation(
    "Currency Validation",
    bool(df["currency"].eq(CURRENCY).all()),
    f"Expected currency: {CURRENCY}"
)

# 7. Numeric and finite values

numeric_values = df[target_metrics].apply(
    pd.to_numeric,
    errors="coerce"
)

record_validation(
    "Numeric Financial Values",
    bool(
        np.isfinite(
            numeric_values.to_numpy(dtype=float)
        ).all()
    ),
    "All financial values must be numeric and finite."
)


# ==================================================
# COMPANY-YEAR FINANCIAL VALIDATION
# ==================================================

for _, row in df.iterrows():

    ticker = row["ticker"]
    year = int(row["fiscal_year"])

    # 8. Fiscal year-end validation

    expected_end = FISCAL_YEAR_ENDS.get(
        ticker, {}
    ).get(year)

    record_validation(
        "Fiscal Year End",
        row["fiscal_year_end"] == expected_end,
        (
            f"Expected: {expected_end}, "
            f"Actual: {row['fiscal_year_end']}"
        ),
        ticker,
        year
    )

    # 9. Balance sheet equation

    expected_assets = (
        row["total_liabilities"]
        + row["shareholders_equity"]
    )

    difference = (
        row["total_assets"] - expected_assets
    )

    record_validation(
        "Balance Sheet Equation",
        abs(difference) <= TOLERANCE,
        f"Difference: ${difference:,.0f}",
        ticker,
        year
    )

    # 10. Gross profit

    expected_gross_profit = (
        row["revenue"]
        - row["cost_of_revenue"]
    )

    difference = (
        row["gross_profit"]
        - expected_gross_profit
    )

    record_validation(
        "Gross Profit Calculation",
        abs(difference) <= TOLERANCE,
        f"Difference: ${difference:,.0f}",
        ticker,
        year
    )

    # 11. Operating income

    expected_operating_income = (
        row["gross_profit"]
        - row["operating_expenses"]
    )

    difference = (
        row["operating_income"]
        - expected_operating_income
    )

    record_validation(
        "Operating Income Calculation",
        abs(difference) <= TOLERANCE,
        f"Difference: ${difference:,.0f}",
        ticker,
        year
    )

    # 12. Free cash flow

    expected_fcf = (
        row["operating_cash_flow"]
        - row["capital_expenditure"]
    )

    difference = (
        row["free_cash_flow"]
        - expected_fcf
    )

    record_validation(
        "Free Cash Flow Calculation",
        abs(difference) <= TOLERANCE,
        f"Difference: ${difference:,.0f}",
        ticker,
        year
    )

    # 13. Nonnegative debt

    record_validation(
        "Nonnegative Debt",
        (
            row["short_term_debt"] >= 0
            and row["long_term_debt"] >= 0
        ),
        (
            f"Short-term: "
            f"${row['short_term_debt']:,.0f}, "
            f"Long-term: "
            f"${row['long_term_debt']:,.0f}"
        ),
        ticker,
        year
    )

    # 14. Current assets consistency

    record_validation(
        "Current Assets Consistency",
        (
            0 <= row["current_assets"]
            <= row["total_assets"]
        ),
        "Current assets must not exceed total assets.",
        ticker,
        year
    )

    # 15. Current liabilities consistency

    record_validation(
        "Current Liabilities Consistency",
        (
            0 <= row["current_liabilities"]
            <= row["total_liabilities"]
        ),
        (
            "Current liabilities must not exceed "
            "total liabilities."
        ),
        ticker,
        year
    )

    # 16. Cash balance consistency

    record_validation(
        "Cash Balance Consistency",
        (
            0 <= row["cash_and_equivalents"]
            <= row["current_assets"]
        ),
        "Cash must not exceed current assets.",
        ticker,
        year
    )

    # 17. Revenue validation

    record_validation(
        "Positive Revenue",
        row["revenue"] > 0,
        f"Revenue: ${row['revenue']:,.0f}",
        ticker,
        year
    )

    # 18. Capital expenditure validation

    record_validation(
        "Capital Expenditure Sign",
        row["capital_expenditure"] >= 0,
        (
            f"Capital expenditure: "
            f"${row['capital_expenditure']:,.0f}"
        ),
        ticker,
        year
    )

    # 19. Short-term debt consistency

    record_validation(
        "Short-Term Debt Consistency",
        (
            row["short_term_debt"]
            <= row["current_liabilities"]
        ),
        "Short-term debt must not exceed current liabilities.",
        ticker,
        year
    )

    # 20. Long-term debt consistency

    noncurrent_liabilities = (
        row["total_liabilities"]
        - row["current_liabilities"]
    )

    record_validation(
        "Long-Term Debt Consistency",
        (
            row["long_term_debt"]
            <= noncurrent_liabilities
        ),
        (
            "Long-term debt must not exceed "
            "noncurrent liabilities."
        ),
        ticker,
        year
    )


# ==================================================
# DEBT SOURCE REVIEW
# ==================================================

if AUDIT_FILE.exists():

    audit_df = pd.read_csv(AUDIT_FILE)

    for _, row in audit_df.iterrows():

        review_status = str(
            row.get("review_status", "Unknown")
        )

        record_validation(
            "Debt Source Verification",
            review_status == "Verified",
            (
                f"Metric: {row['metric']} | "
                f"Review status: {review_status}"
            ),
            row["ticker"],
            row["fiscal_year"],
            warning=True
        )

else:

    record_validation(
        "Debt Audit Log",
        False,
        "Debt reconciliation audit log not found."
    )

# Cross-company debt definitions still require review.

record_validation(
    "Cross-Company Debt Definition Review",
    False,
    (
        "Verify reported and calculated debt components "
        "against original annual reports for all years."
    ),
    warning=True
)


# ==================================================
# SAVE VALIDATION REPORT
# ==================================================

results_df = pd.DataFrame(validation_results)

results_df.to_csv(
    OUTPUT_FILE,
    index=False
)

total_checks = len(results_df)

passed_checks = int(
    results_df["status"].eq("PASS").sum()
)

failed_checks = int(
    results_df["status"].eq("FAIL").sum()
)

warning_checks = int(
    results_df["status"].eq("WARNING").sum()
)

pass_rate = (
    passed_checks / total_checks
) * 100


# ==================================================
# DISPLAY VALIDATION SUMMARY
# ==================================================

print("\n" + "=" * 70)
print("FINANCIAL VALIDATION SUMMARY")
print("=" * 70)

print(f"Companies: {df['ticker'].nunique()}")
print(f"Financial records: {len(df)}")
print(f"Financial metrics: {len(target_metrics)}")

print(f"\nTotal validation checks: {total_checks}")
print(f"Passed checks: {passed_checks}")
print(f"Failed checks: {failed_checks}")
print(f"Warnings: {warning_checks}")
print(f"Validation pass rate: {pass_rate:.2f}%")

issues = results_df[
    results_df["status"] != "PASS"
]

if not issues.empty:

    print("\n" + "=" * 70)
    print("ISSUES REQUIRING REVIEW")
    print("=" * 70)

    print(issues.to_string(index=False))

print("\n" + "=" * 70)
print("VALIDATION STATUS")
print("=" * 70)

if failed_checks > 0:

    print("FAILED: Financial corrections required.")

elif warning_checks > 0:

    print("CONDITIONAL PASS: Source review required.")

else:

    print("PASSED: All implemented checks passed.")

print(f"\nValidation report: {OUTPUT_FILE}")

print("\nFinancial data validation completed.")
