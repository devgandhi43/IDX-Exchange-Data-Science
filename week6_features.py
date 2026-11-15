import pandas as pd

sold = pd.read_csv("data/processed/sold_clean.csv", low_memory=False)

for col in ["CloseDate", "PurchaseContractDate", "ListingContractDate"]:
    sold[col] = pd.to_datetime(sold[col], errors="coerce")

for col in ["ClosePrice", "OriginalListPrice", "ListPrice", "LivingArea", "DaysOnMarket"]:
    sold[col] = pd.to_numeric(sold[col], errors="coerce")

sold["PriceRatio"] = sold["ClosePrice"] / sold["ListPrice"].replace(0, float("nan"))
sold["CloseToOriginalListRatio"] = sold["ClosePrice"] / sold["OriginalListPrice"].replace(0, float("nan"))
sold["PricePerSqFt"] = sold["ClosePrice"] / sold["LivingArea"].replace(0, float("nan"))
sold["Year"] = sold["CloseDate"].dt.year
sold["Month"] = sold["CloseDate"].dt.month
sold["YrMo"] = sold["CloseDate"].dt.to_period("M").astype(str)
sold["ListingToContractDays"] = (sold["PurchaseContractDate"] - sold["ListingContractDate"]).dt.days
sold["ContractToCloseDays"] = (sold["CloseDate"] - sold["PurchaseContractDate"]).dt.days

metrics = ["PriceRatio", "CloseToOriginalListRatio", "PricePerSqFt", "DaysOnMarket", "Year", "Month", "YrMo", "ListingToContractDays", "ContractToCloseDays"]
print("SAMPLE OUTPUT")
print(sold[["ClosePrice"] + metrics].head(10).to_string())

print()
print(sold[metrics].describe().T[["count", "mean", "50%", "min", "max"]])


def summary(group):
    return sold.groupby(group).agg(
        sales=("ClosePrice", "count"),
        median_price=("ClosePrice", "median"),
        median_price_per_sqft=("PricePerSqFt", "median"),
        median_price_ratio=("PriceRatio", "median"),
        median_days_on_market=("DaysOnMarket", "median"),
    ).sort_values("sales", ascending=False)


print()
print("SUMMARY BY PROPERTY SUBTYPE")
print(summary("PropertySubType").round(2))

print()
print("SUMMARY BY COUNTY (TOP 10)")
print(summary("CountyOrParish").head(10).round(2))

sold.to_csv("data/processed/sold_features.csv", index=False)