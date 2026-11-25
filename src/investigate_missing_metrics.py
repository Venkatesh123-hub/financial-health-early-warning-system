
import json
from pathlib import Path

from financial_metrics import (
    COMPANIES,
    FISCAL_YEAR_ENDS
)

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"

DEBT_TAGS = [
    "CommercialPaper",
    "DebtCurrent",
    "ShortTermBorrowings",
    "OtherShortTermBorrowings",
    "LongTermDebt",
    "LongTermDebtCurrent",
    "LongTermDebtNoncurrent",
    "DebtInstrumentUnamortizedDiscountPremiumAndDebtIssuanceCostsNet",
    "FinanceLeaseLiability",
    "FinanceLeaseLiabilityCurrent",
    "FinanceLeaseLiabilityNoncurrent",
    "LongTermDebtAndCapitalLeaseObligations",
    "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities"
]

for ticker, company in COMPANIES.items():

    file_path = RAW_DIR / f"{ticker}_financial_data.json"

    with open(file_path, encoding="utf-8") as file:

        data = json.load(file)

    facts = data["facts"]["us-gaap"]

    print("\n" + "=" * 90)
    print(f"{company.upper()} ({ticker})")
    print("=" * 90)

    for year, fiscal_end in FISCAL_YEAR_ENDS[ticker].items():

        print(f"\nFiscal year: {year} | End: {fiscal_end}")
        print("-" * 90)

        for tag in DEBT_TAGS:

            unit_records = (
                facts.get(tag, {})
                .get("units", {})
                .get("USD", [])
            )

            records = [
                record
                for record in unit_records
                if record.get("form") == "10-K"
                and record.get("end") == fiscal_end
                and not record.get("start")
                and record.get("val") is not None
            ]

            if not records:
                continue

            latest = max(
                records,
                key=lambda record: (
                    record.get("filed", ""),
                    record.get("accn", "")
                )
            )

            value = latest["val"] / 1_000_000

            print(
                f"{tag}: "
                f"${value:,.2f}M"
                f" | Filed: {latest.get('filed')}"
                f" | Accession: {latest.get('accn')}"
            )

print("\n" + "=" * 90)
print("DEBT COMPONENT INVESTIGATION COMPLETED")
print("=" * 90)
