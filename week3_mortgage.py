import pandas as pd

# ANSWERS
# Sold: rows 495,321; null after merge 0
# Listings: rows 625,325; null after merge 0

mortgage = pd.read_csv("https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US", parse_dates=["observation_date"])
mortgage.columns = ["date", "rate_30yr_fixed"]
mortgage["year_month"] = mortgage["date"].dt.to_period("M")
mortgage_monthly = mortgage.groupby("year_month")["rate_30yr_fixed"].mean().reset_index()

sold = pd.read_csv("data/processed/sold_filtered.csv", low_memory=False)
listings = pd.read_csv("data/processed/listings_filtered.csv", low_memory=False)

sold["year_month"] = pd.to_datetime(sold["CloseDate"], errors="coerce", utc=True).dt.tz_localize(None).dt.to_period("M")
listings["year_month"] = pd.to_datetime(listings["ListingContractDate"], errors="coerce", utc=True).dt.tz_localize(None).dt.to_period("M")

sold_with_rates = sold.merge(mortgage_monthly, on="year_month", how="left")
listings_with_rates = listings.merge(mortgage_monthly, on="year_month", how="left")

print("Sold rows:", len(sold_with_rates), "| null rates:", sold_with_rates["rate_30yr_fixed"].isna().sum(), "| missing CloseDate:", sold["CloseDate"].isna().sum())
print("Listings rows:", len(listings_with_rates), "| null rates:", listings_with_rates["rate_30yr_fixed"].isna().sum(), "| missing ListingContractDate:", listings["ListingContractDate"].isna().sum())

print(sold_with_rates[["CloseDate", "year_month", "ClosePrice", "rate_30yr_fixed"]].head())

sold_with_rates.to_csv("data/processed/sold_with_rates.csv", index=False)
listings_with_rates.to_csv("data/processed/listings_with_rates.csv", index=False)