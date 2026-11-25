
import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# Project directory
BASE_DIR = Path(__file__).resolve().parents[1]

# Load environment variables
load_dotenv(BASE_DIR / ".env")

SEC_EMAIL = os.getenv("SEC_EMAIL", "").strip()

if "@" not in SEC_EMAIL or SEC_EMAIL.endswith("@example.com"):
    raise ValueError("Configure a valid SEC_EMAIL in the .env file")

# Company identification numbers
COMPANIES = {
    "MSFT": "0000789019",
    "AAPL": "0000320193",
    "GOOGL": "0001652044"
}

# SEC API request headers
HEADERS = {
    "User-Agent": f"Financial Portfolio Project {SEC_EMAIL}",
    "Accept": "application/json"
}

# Raw data directory
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def fetch_financial_data(ticker, cik):
    url = (
        "https://data.sec.gov/api/xbrl/"
        f"companyfacts/CIK{cik}.json"
    )

    print(f"Fetching financial data for {ticker}...")

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=60
    )

    response.raise_for_status()
    data = response.json()

    file_path = RAW_DATA_DIR / f"{ticker}_financial_data.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print(f"Successfully saved: {file_path}")


def main():
    failed = []

    for ticker, cik in COMPANIES.items():
        try:
            fetch_financial_data(ticker, cik)

        except (requests.RequestException, OSError, ValueError) as error:
            print(f"Error fetching {ticker}: {error}")
            failed.append(ticker)

        time.sleep(1)

    if failed:
        raise SystemExit(f"Download failed for: {', '.join(failed)}")

    print("All financial datasets downloaded successfully.")


if __name__ == "__main__":
    main()
