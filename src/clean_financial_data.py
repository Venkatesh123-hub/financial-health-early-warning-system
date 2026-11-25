
import json
from datetime import date
from pathlib import Path

import pandas as pd

from financial_metrics import (
    COMPANIES,
    FINANCIAL_METRICS,
    FISCAL_YEAR_ENDS,
    BALANCE_SHEET,
    DEBT_COMPONENTS,
    CURRENCY
)

# Project directories
BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def load_company_data(ticker):

    file_path = (
        RAW_DATA_DIR / f"{ticker}_financial_data.json"
    )

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def extract_annual_value(facts, tags, fiscal_end, instant):

    for tag in tags:

        records = (
            facts.get(tag, {})
            .get("units", {})
            .get(CURRENCY, [])
        )

        valid_records = []

        for record in records:

            if record.get("form") != "10-K":
                continue

            if record.get("end") != fiscal_end:
                continue

            if record.get("val") is None:
                continue

            if instant:

                # Balance sheet: point-in-time value
                if "start" in record:
                    continue

            else:

                # Income and cash flow: full-year value
                if "start" not in record:
                    continue

                start = date.fromisoformat(
                    record["start"]
                )

                end = date.fromisoformat(
                    record["end"]
                )

                duration = (end - start).days + 1

                if not 350 <= duration <= 380:
                    continue

            valid_records.append(record)

        if valid_records:

            latest_record = max(
                valid_records,
                key=lambda item: (
                    item.get("filed", ""),
                    item.get("accn", "")
                )
            )

            return latest_record["val"], tag

    return None, None


def extract_financial_data():

    financial_rows = []
    source_rows = []

    all_metrics = {
        **FINANCIAL_METRICS,
        **DEBT_COMPONENTS
    }

    for ticker, company in COMPANIES.items():

        data = load_company_data(ticker)
        facts = data["facts"]["us-gaap"]

        print(f"\nProcessing {company} ({ticker})")

        for year, fiscal_end in FISCAL_YEAR_ENDS[ticker].items():

            row = {
                "ticker": ticker,
                "company": company,
                "fiscal_year": year,
                "fiscal_year_end": fiscal_end,
                "currency": CURRENCY
            }

            for metric, tags in all_metrics.items():

                instant = (
                    metric in BALANCE_SHEET
                    or metric in DEBT_COMPONENTS
                )

                value, source_tag = extract_annual_value(
                    facts,
                    tags,
                    fiscal_end,
                    instant
                )

                row[metric] = value

                source_rows.append({
                    "ticker": ticker,
                    "fiscal_year": year,
                    "fiscal_year_end": fiscal_end,
                    "metric": metric,
                    "source_tag": source_tag,
                    "value": value,
                    "status": (
                        "Extracted"
                        if value is not None
                        else "Missing"
                    )
                })

            financial_rows.append(row)

            print(f"  Fiscal year {year}: Processed")

    df = pd.DataFrame(financial_rows)
    sources_df = pd.DataFrame(source_rows)

    # Save preliminary financial dataset
    financial_path = (
        PROCESSED_DATA_DIR
        / "annual_financial_data_preliminary.csv"
    )

    df.to_csv(financial_path, index=False)

    # Save accounting tag traceability report
    sources_path = (
        PROCESSED_DATA_DIR
        / "financial_metric_sources.csv"
    )

    sources_df.to_csv(sources_path, index=False)

    print("\n" + "=" * 70)
    print("ANNUAL FINANCIAL EXTRACTION SUMMARY")
    print("=" * 70)

    print(f"Companies: {df['ticker'].nunique()}")
    print(f"Financial records: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    print(f"Metric extraction checks: {len(sources_df)}")

    print(
        f"Extracted values: "
        f"{(sources_df['status'] == 'Extracted').sum()}"
    )

    print(
        f"Missing values: "
        f"{(sources_df['status'] == 'Missing').sum()}"
    )

    print("\nMissing direct financial metrics:")

    missing = sources_df[
        (sources_df["status"] == "Missing")
        & sources_df["metric"].isin(FINANCIAL_METRICS)
    ]

    if missing.empty:
        print("No missing direct metrics.")

    else:
        print(
            missing[
                ["ticker", "fiscal_year", "metric"]
            ].to_string(index=False)
        )

    print(f"\nFinancial dataset saved to: {financial_path}")
    print(f"Source report saved to: {sources_path}")

    print("\nAnnual financial extraction completed.")


if __name__ == "__main__":
    extract_financial_data()
