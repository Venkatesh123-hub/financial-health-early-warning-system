
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

for file_path in sorted(RAW_DATA_DIR.glob("*.json")):

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    print("=" * 60)
    print(f"File Name: {file_path.name}")
    print(f"Company Name: {data.get('entityName')}")
    print(f"CIK: {data.get('cik')}")

    facts = data.get("facts", {})
    financial_facts = facts.get("us-gaap", {})

    print(f"Available Taxonomies: {list(facts.keys())}")
    print(f"Total US-GAAP Metrics: {len(financial_facts)}")

    print("\nSample Financial Metrics:")

    for metric in list(financial_facts.keys())[:10]:
        print(f" - {metric}")

    print()

print("Financial data inspection completed.")
