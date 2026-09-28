"""
IDX Exchange - Week 1: Monthly Dataset Aggregation

Combines every monthly CRMLS Sold and Listing file from January 2024 through
the most recently completed calendar month, filters both to Residential
properties, and saves the results as new CSVs.

Folder layout expected (run this script from the repo root):
    data/raw/        <- put the CRMLSSoldYYYYMM.csv / CRMLSListingYYYYMM.csv files here
    data/processed/  <- combined outputs are written here (created automatically)

ROW COUNTS (fill these in after you run the script - copy from the printed output)
--------------------------------------------------------------------------------
Sold:
    Months loaded:                      28
    Rows before concat (sum of files):  615,707
    Rows after concat:                  615,707
    Rows after Residential filter:      414,054
Listings:
    Months loaded:                      28
    Rows before concat (sum of files):  822,087
    Rows after concat:                  822,087
    Rows after Residential filter:      522,931
"""

from datetime import date
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")
START_MONTH = pd.Period("2024-01", freq="M")
# Most recently completed calendar month = the month before today
END_MONTH = pd.Period("2026-04", freq="M")


def expected_months():
    """Every YYYYMM string from START_MONTH through END_MONTH."""
    return [p.strftime("%Y%m") for p in pd.period_range(START_MONTH, END_MONTH, freq="M")]


def combine(prefix):
    """Load one CSV per month for the given prefix and stack them into one DataFrame."""
    months = expected_months()
    frames = []
    missing = []
    rows_before = 0
    counts = {}

    for m in months:
        # Some months on the FTP are named with a "_filled" suffix (e.g. CRMLSSold202401_filled.csv)
        candidates = [RAW_DIR / f"{prefix}{m}.csv", RAW_DIR / f"{prefix}{m}_filled.csv"]
        path = next((p for p in candidates if p.exists()), None)
        if path is None:
            missing.append(m)
            continue
        df = pd.read_csv(path, low_memory=False)
        print(f"  {path.name}: {len(df):,} rows")
        counts[m] = len(df)
        rows_before += len(df)
        frames.append(df)

    if missing:
        print(f"  WARNING - missing months for {prefix}: {', '.join(missing)}")

    # Flag months with far fewer rows than typical - usually an incomplete download
    if counts:
        typical = pd.Series(counts).median()
        small = [f"{m} ({n:,})" for m, n in counts.items() if n < 0.5 * typical]
        if small:
            print(f"  WARNING - suspiciously small months (re-download?): {', '.join(small)}")

    if not frames:
        raise FileNotFoundError(f"No {prefix} files found in {RAW_DIR.resolve()}")

    combined = pd.concat(frames, ignore_index=True)

    # Sanity check: concatenation should neither add nor drop rows
    assert len(combined) == rows_before, "Row count changed during concat!"

    print(f"  Months loaded: {len(frames)} of {len(months)}")
    print(f"  Rows before concat (sum of files): {rows_before:,}")
    print(f"  Rows after concat:                 {len(combined):,}")
    return combined


def filter_residential(df, label):
    """Keep only PropertyType == 'Residential'."""
    print(f"  PropertyType counts ({label}):")
    print(df["PropertyType"].value_counts(dropna=False).to_string())
    residential = df[df["PropertyType"] == "Residential"].copy()
    print(f"  Rows before Residential filter: {len(df):,}")
    print(f"  Rows after Residential filter:  {len(residential):,}")
    return residential


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Date range: {START_MONTH} through {END_MONTH}\n")

    print("=== SOLD ===")
    sold = combine("CRMLSSold")
    sold_res = filter_residential(sold, "sold")
    sold_res.to_csv(OUT_DIR / "sold_combined_residential.csv", index=False)

    print("\n=== LISTINGS ===")
    listings = combine("CRMLSListing")
    listings_res = filter_residential(listings, "listings")
    listings_res.to_csv(OUT_DIR / "listings_combined_residential.csv", index=False)

    print(f"\nSaved combined Residential files to {OUT_DIR.resolve()}")


if __name__ == "__main__":
    main()