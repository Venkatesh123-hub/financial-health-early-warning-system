
from pathlib import Path

import pandas as pd

from financial_metrics import FINANCIAL_METRICS

# ==================================================
# PROJECT CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = BASE_DIR / "data" / "processed"
EXCEL_DIR = BASE_DIR / "excel"

EXCEL_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = (
    PROCESSED_DIR
    / "annual_financial_data_reconciled.csv"
)

VALIDATION_FILE = (
    PROCESSED_DIR
    / "financial_validation_report.csv"
)

AUDIT_FILE = (
    PROCESSED_DIR
    / "debt_reconciliation_log.csv"
)

CSV_FILE = (
    PROCESSED_DIR
    / "annual_financial_data.csv"
)

EXCEL_FILE = (
    EXCEL_DIR
    / "annual_financial_data.xlsx"
)

QUALITY_FILE = (
    PROCESSED_DIR
    / "financial_data_quality_notes.csv"
)

# ==================================================
# LOAD FINANCIAL DATA
# ==================================================

df = pd.read_csv(INPUT_FILE)

validation = pd.read_csv(VALIDATION_FILE)

audit = pd.read_csv(AUDIT_FILE)

# Prevent export if accounting checks failed

failed_checks = int(
    validation["status"].eq("FAIL").sum()
)

if failed_checks > 0:
    raise ValueError(
        "Export blocked: Financial validation failed."
    )

# ==================================================
# SELECT TARGET FINANCIAL METRICS
# ==================================================

metadata_columns = [
    "ticker",
    "company",
    "fiscal_year",
    "fiscal_year_end",
    "currency"
]

financial_columns = [
    *FINANCIAL_METRICS.keys(),
    "free_cash_flow"
]

final_columns = (
    metadata_columns + financial_columns
)

final_df = df[final_columns].copy()

final_df = final_df.sort_values(
    ["ticker", "fiscal_year"]
).reset_index(drop=True)

# ==================================================
# VERIFY DATA COMPLETENESS
# ==================================================

missing_values = int(
    final_df[financial_columns]
    .isna()
    .sum()
    .sum()
)

if missing_values > 0:
    raise ValueError(
        f"Missing financial values: {missing_values}"
    )

if len(final_df) != 15:
    raise ValueError(
        "Expected exactly 15 financial records."
    )

# ==================================================
# DATA QUALITY DOCUMENTATION
# ==================================================

quality_notes = pd.DataFrame([

    {
        "ticker": "MSFT",
        "fiscal_year": 2021,
        "metric": "short_term_debt",
        "status": "Provisional",
        "details": (
            "Current portion of long-term debt confirmed. "
            "Other short-term borrowings not independently "
            "confirmed."
        ),
        "source": (
            "https://www.microsoft.com/investor/reports/ar22/"
        )
    },

    {
        "ticker": "MSFT",
        "fiscal_year": 2022,
        "metric": "short_term_debt",
        "status": "Provisional",
        "details": (
            "Current portion of long-term debt confirmed. "
            "Commercial paper not separately reported."
        ),
        "source": (
            "https://www.microsoft.com/investor/reports/ar22/"
        )
    },

    {
        "ticker": "GOOGL",
        "fiscal_year": 2021,
        "metric": "long_term_debt",
        "status": "Calculated - pending source review",
        "details": (
            "Calculated noncurrent borrowings of "
            "12844 million USD, excluding finance leases."
        ),
        "source": (
            "https://www.sec.gov/Archives/edgar/data/"
            "1652044/000165204423000016/goog-20221231.htm"
        )
    },

    {
        "ticker": "GOOGL",
        "fiscal_year": 2022,
        "metric": "long_term_debt",
        "status": "Calculated - pending source review",
        "details": (
            "Calculated noncurrent borrowings of "
            "12857 million USD, excluding finance leases."
        ),
        "source": (
            "https://www.sec.gov/Archives/edgar/data/"
            "1652044/000165204423000016/goog-20221231.htm"
        )
    },

    {
        "ticker": "ALL",
        "fiscal_year": "ALL",
        "metric": "debt_definition",
        "status": "Source review required",
        "details": (
            "Debt metrics aim to exclude finance leases. "
            "Cross-company comparability requires "
            "additional verification."
        ),
        "source": "SEC EDGAR Company Facts and annual reports"
    },

    {
        "ticker": "ALL",
        "fiscal_year": "ALL",
        "metric": "financial_data",
        "status": "Conditional pass",
        "details": (
            "All implemented accounting checks passed. "
            "Data completeness does not establish "
            "independent source accuracy."
        ),
        "source": "Financial validation report"
    }

])

# ==================================================
# DATA DICTIONARY
# ==================================================

data_dictionary = pd.DataFrame([

    {
        "column": column,
        "category": (
            "Metadata"
            if column in metadata_columns
            else "Financial metric"
        ),
        "unit": (
            "USD"
            if column in financial_columns
            else "Not applicable"
        ),
        "description": (
            "Operating cash flow minus capital expenditure"
            if column == "free_cash_flow"
            else column.replace("_", " ").capitalize()
        )
    }

    for column in final_columns

])

# ==================================================
# EXPORT CSV FILES
# ==================================================

final_df.to_csv(CSV_FILE, index=False)

quality_notes.to_csv(
    QUALITY_FILE,
    index=False
)

# ==================================================
# EXPORT EXCEL WORKBOOK
# ==================================================

with pd.ExcelWriter(
    EXCEL_FILE,
    engine="openpyxl"
) as writer:

    final_df.to_excel(
        writer,
        sheet_name="Financial Data",
        index=False
    )

    data_dictionary.to_excel(
        writer,
        sheet_name="Data Dictionary",
        index=False
    )

    validation.to_excel(
        writer,
        sheet_name="Validation Report",
        index=False
    )

    audit.to_excel(
        writer,
        sheet_name="Debt Reconciliation",
        index=False
    )

    quality_notes.to_excel(
        writer,
        sheet_name="Data Quality Notes",
        index=False
    )

# ==================================================
# EXPORT SUMMARY
# ==================================================

print("=" * 70)
print("FINANCIAL DATA EXPORT SUMMARY")
print("=" * 70)

print(f"Companies: {final_df['ticker'].nunique()}")
print(f"Financial records: {len(final_df)}")
print(f"Financial metrics: {len(financial_columns)}")
print(f"Total columns: {len(final_df.columns)}")

print(
    f"Total financial values: "
    f"{len(final_df) * len(financial_columns)}"
)

print(f"Missing values: {missing_values}")
print(f"Failed validation checks: {failed_checks}")

print("\nDataset status: CONDITIONAL PASS")

print(f"\nCSV dataset: {CSV_FILE}")
print(f"Excel workbook: {EXCEL_FILE}")
print(f"Data quality notes: {QUALITY_FILE}")

print("\nFinancial data export completed successfully.")
