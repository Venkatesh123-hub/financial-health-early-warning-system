
# Financial Health & Early Warning System
# Financial metric mapping configuration

START_YEAR = 2021
END_YEAR = 2025
CURRENCY = "USD"

# Target companies
COMPANIES = {
    "MSFT": "Microsoft",
    "AAPL": "Apple",
    "GOOGL": "Alphabet"
}

# Fiscal year-end dates
FISCAL_YEAR_ENDS = {
    "MSFT": {
        2021: "2021-06-30",
        2022: "2022-06-30",
        2023: "2023-06-30",
        2024: "2024-06-30",
        2025: "2025-06-30"
    },
    "AAPL": {
        2021: "2021-09-25",
        2022: "2022-09-24",
        2023: "2023-09-30",
        2024: "2024-09-28",
        2025: "2025-09-27"
    },
    "GOOGL": {
        2021: "2021-12-31",
        2022: "2022-12-31",
        2023: "2023-12-31",
        2024: "2024-12-31",
        2025: "2025-12-31"
    }
}

# Income statement metrics
INCOME_STATEMENT = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet"
    ],
    "cost_of_revenue": [
        "CostOfRevenue",
        "CostOfGoodsAndServicesSold"
    ],
    "gross_profit": [
        "GrossProfit"
    ],
    "operating_expenses": [
        "OperatingExpenses"
    ],
    "operating_income": [
        "OperatingIncomeLoss"
    ],
    "net_income": [
        "NetIncomeLoss"
    ]
}

# Balance sheet metrics
BALANCE_SHEET = {
    "total_assets": [
        "Assets"
    ],
    "total_liabilities": [
        "Liabilities"
    ],
    "shareholders_equity": [
        "StockholdersEquity"
    ],
    "current_assets": [
        "AssetsCurrent"
    ],
    "current_liabilities": [
        "LiabilitiesCurrent"
    ],
    "cash_and_equivalents": [
        "CashAndCashEquivalentsAtCarryingValue"
    ],
    "short_term_debt": [
        "DebtCurrent"
    ],
    "long_term_debt": [
        "LongTermDebtNoncurrent"
    ],
    "retained_earnings": [
        "RetainedEarningsAccumulatedDeficit"
    ]
}

# Cash flow statement metrics
CASH_FLOW_STATEMENT = {
    "operating_cash_flow": [
        "NetCashProvidedByUsedInOperatingActivities"
    ],
    "investing_cash_flow": [
        "NetCashProvidedByUsedInInvestingActivities"
    ],
    "financing_cash_flow": [
        "NetCashProvidedByUsedInFinancingActivities"
    ],
    "capital_expenditure": [
        "PaymentsToAcquirePropertyPlantAndEquipment"
    ]
}

# Combine financial metrics
FINANCIAL_METRICS = {
    **INCOME_STATEMENT,
    **BALANCE_SHEET,
    **CASH_FLOW_STATEMENT
}

# Calculated financial metrics
CALCULATED_METRICS = {
    "free_cash_flow": (
        "operating_cash_flow - capital_expenditure"
    )
}

# Supporting debt component mappings
DEBT_COMPONENTS = {
    "commercial_paper": [
        "CommercialPaper"
    ],
    "current_long_term_debt": [
        "LongTermDebtCurrent"
    ],
    "noncurrent_long_term_debt": [
        "LongTermDebtNoncurrent"
    ],
    "other_short_term_borrowings": [
        "OtherShortTermBorrowings"
    ],
    "reported_total_long_term_debt": [
        "LongTermDebt"
    ]
}

# Candidate fallback calculation rules
# Apply only after verifying component definitions
# and reporting periods.
FALLBACK_FORMULAS = {
    "gross_profit": (
        "revenue - cost_of_revenue"
    ),
    "operating_expenses": (
        "gross_profit - operating_income"
    ),
    "short_term_debt": (
        "commercial_paper + current_long_term_debt"
    ),
    "long_term_debt": (
        "reported_total_long_term_debt "
        "- current_long_term_debt"
    )
}

# Verify configuration
if __name__ == "__main__":

    print("Financial metric configuration loaded.")

    print(f"Companies: {len(COMPANIES)}")

    print(f"Fiscal years: {START_YEAR}-{END_YEAR}")

    print(f"Currency: {CURRENCY}")

    print(
        f"Income statement metrics: "
        f"{len(INCOME_STATEMENT)}"
    )

    print(
        f"Balance sheet metrics: "
        f"{len(BALANCE_SHEET)}"
    )

    print(
        f"Cash flow metrics: "
        f"{len(CASH_FLOW_STATEMENT)}"
    )

    print(
        f"Direct financial metrics: "
        f"{len(FINANCIAL_METRICS)}"
    )

    print(
        f"Calculated metrics: "
        f"{len(CALCULATED_METRICS)}"
    )

    print(
        f"Total financial metrics: "
        f"{len(FINANCIAL_METRICS) + len(CALCULATED_METRICS)}"
    )

    print(
        f"Supporting debt components: "
        f"{len(DEBT_COMPONENTS)}"
    )

    print(
        f"Fallback calculation rules: "
        f"{len(FALLBACK_FORMULAS)}"
    )

    print("Configuration verification completed.")
