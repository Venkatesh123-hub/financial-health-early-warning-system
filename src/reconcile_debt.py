
from pathlib import Path

import pandas as pd

from financial_metrics import FINANCIAL_METRICS

# Project directories
BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

INPUT_FILE = (
    PROCESSED_DATA_DIR
    / "annual_financial_data_transformed.csv"
)

OUTPUT_FILE = (
    PROCESSED_DATA_DIR
    / "annual_financial_data_reconciled.csv"
)

AUDIT_FILE = (
    PROCESSED_DATA_DIR
    / "debt_reconciliation_log.csv"
)

# Load transformed financial dataset
df = pd.read_csv(INPUT_FILE)

audit_log = []

# ==================================================
# MICROSOFT DEBT RECONCILIATION
# ==================================================

MSFT_SOURCE_URL = (
    "https://www.microsoft.com/investor/reports/ar22/"
)

for year in [2021, 2022]:

    mask = (
        (df["ticker"] == "MSFT")
        & (df["fiscal_year"] == year)
    )

    if mask.sum() != 1:
        raise ValueError(
            f"Expected one Microsoft record for {year}"
        )

    index = df.index[mask][0]

    total_debt = df.at[
        index, "reported_total_long_term_debt"
    ]

    noncurrent_debt = df.at[
        index, "noncurrent_long_term_debt"
    ]

    reported_current_debt = df.at[
        index, "current_long_term_debt"
    ]

    components = [
        total_debt,
        noncurrent_debt,
        reported_current_debt
    ]

    if any(pd.isna(value) for value in components):
        raise ValueError(
            f"Missing debt components for MSFT {year}"
        )

    calculated_debt = total_debt - noncurrent_debt

    if calculated_debt != reported_current_debt:
        raise ValueError(
            f"Debt reconciliation failed for MSFT {year}"
        )

    original_value = df.at[index, "short_term_debt"]

    df.at[index, "short_term_debt"] = calculated_debt

    audit_log.append({
        "ticker": "MSFT",
        "fiscal_year": year,
        "metric": "short_term_debt",
        "original_value": original_value,
        "reconciled_value": calculated_debt,
        "method": "Annual report debt reconciliation",
        "formula": "Total long-term debt - Noncurrent debt",
        "source": "Microsoft 2022 Annual Report",
        "source_section": "Note 11 - Debt",
        "accession": "0001564590-22-026876",
        "source_url": MSFT_SOURCE_URL,
        "validation": "Matched reported current debt",
        "review_status": "Pending final verification",
        "limitations": (
            "Current portion of long-term debt only. "
            "Other short-term borrowings require verification."
        )
    })

    print(
        f"MSFT {year}: "
        f"${calculated_debt / 1_000_000:,.2f} million"
        f" | Provisionally reconciled"
    )


# ==================================================
# ALPHABET DEBT RECONCILIATION
# ==================================================

# Candidate historical notes components
# Subject to final annual report verification

ALPHABET_DEBT = {
    2021: {
        "principal": 13_000_000_000,
        "issuance_costs": 156_000_000
    },
    2022: {
        "principal": 13_000_000_000,
        "issuance_costs": 143_000_000
    }
}

ALPHABET_SOURCE_URL = (
    "https://www.sec.gov/Archives/edgar/data/"
    "1652044/000165204423000016/goog-20221231.htm"
)

for year, components in ALPHABET_DEBT.items():

    mask = (
        (df["ticker"] == "GOOGL")
        & (df["fiscal_year"] == year)
    )

    if mask.sum() != 1:
        raise ValueError(
            f"Expected one Alphabet record for {year}"
        )

    index = df.index[mask][0]

    principal = components["principal"]
    issuance_costs = components["issuance_costs"]

    current_debt = df.at[
        index, "current_long_term_debt"
    ]

    if pd.isna(current_debt):
        raise ValueError(
            f"Missing current debt for GOOGL {year}"
        )

    calculated_debt = (
        principal
        - issuance_costs
        - current_debt
    )

    if calculated_debt < 0:
        raise ValueError(
            f"Invalid long-term debt for GOOGL {year}"
        )

    original_value = df.at[index, "long_term_debt"]

    df.at[index, "long_term_debt"] = calculated_debt

    audit_log.append({
        "ticker": "GOOGL",
        "fiscal_year": year,
        "metric": "long_term_debt",
        "original_value": original_value,
        "reconciled_value": calculated_debt,
        "method": "Candidate annual report calculation",
        "formula": (
            "Notes principal - Unamortized costs "
            "- Current portion of notes"
        ),
        "source": "Alphabet 2022 Form 10-K",
        "source_section": "Note 6 - Debt",
        "accession": "0001652044-23-000016",
        "source_url": ALPHABET_SOURCE_URL,
        "validation": "Arithmetic calculation completed",
        "review_status": "Pending final verification",
        "limitations": (
            "Candidate notes-only carrying amount. "
            "Debt components and definitions require "
            "final source reconciliation."
        )
    })

    print(
        f"GOOGL {year}: "
        f"${calculated_debt / 1_000_000:,.2f} million"
        f" | Provisionally reconciled"
    )


# ==================================================
# SAVE RECONCILED DATASET AND AUDIT LOG
# ==================================================

df.to_csv(OUTPUT_FILE, index=False)

audit_df = pd.DataFrame(audit_log)

audit_df.to_csv(AUDIT_FILE, index=False)

print("\n" + "=" * 70)
print("DEBT RECONCILIATION SUMMARY")
print("=" * 70)

print(f"Reconciled values: {len(audit_log)}")
print(f"Reconciled dataset: {OUTPUT_FILE}")
print(f"Audit log: {AUDIT_FILE}")

print("\nDebt reconciliation completed.")


# ==================================================
# DATA COMPLETENESS VERIFICATION
# ==================================================

target_metrics = [
    *FINANCIAL_METRICS.keys(),
    "free_cash_flow"
]

total_values = len(df) * len(target_metrics)

missing_values = int(
    df[target_metrics].isna().sum().sum()
)

available_values = total_values - missing_values

completeness = (
    available_values / total_values
) * 100

print("\n" + "=" * 70)
print("DATA COMPLETENESS VERIFICATION")
print("=" * 70)

print(f"Companies: {df['ticker'].nunique()}")
print(f"Financial records: {len(df)}")
print(f"Financial metrics: {len(target_metrics)}")
print(f"Total target values: {total_values}")
print(f"Available values: {available_values}")
print(f"Missing values: {missing_values}")
print(f"Data completeness: {completeness:.2f}%")

if missing_values == 0:
    print("\nAll target financial values populated.")
    print("Financial accuracy validation is still required.")
else:
    print("\nOutstanding missing values detected.")

print("\nFinancial debt reconciliation pipeline completed.")
