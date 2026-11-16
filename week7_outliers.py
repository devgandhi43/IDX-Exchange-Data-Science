import pandas as pd

# Rows before: 495,085 | rows after: 418,261 | rows removed: 76,824 (15.5%)
# Median ClosePrice before: 825,000 | after: 785,000
# Median LivingArea before: 1,648 | after: 1,574
# Median DaysOnMarket before: 19 | after: 16
# Filtering removed 76,824 rows (15.5%)
sold = pd.read_csv("data/processed/sold_features.csv", low_memory=False)

fields = ["ClosePrice", "LivingArea", "DaysOnMarket"]

print("PERCENTILES")
print(sold[fields].describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]).round(2))

print()
print("IQR BOUNDS")
for col in fields:
    q1 = sold[col].quantile(0.25)
    q3 = sold[col].quantile(0.75)
    iqr = q3 - q1
    low = q1 - 1.5 * iqr
    high = q3 + 1.5 * iqr
    sold[col + "_outlier"] = (sold[col] < low) | (sold[col] > high)
    print(col, "| Q1:", round(q1, 2), "| Q3:", round(q3, 2), "| lower:", round(low, 2), "| upper:", round(high, 2), "| outliers:", sold[col + "_outlier"].sum())

flags = [col + "_outlier" for col in fields]
sold["any_outlier"] = sold[flags].any(axis=1)
clean = sold[~sold["any_outlier"]]

sold.to_csv("data/processed/sold_flagged.csv", index=False)
clean.to_csv("data/processed/sold_outlier_filtered.csv", index=False)

print()
print("BEFORE VS AFTER")
print("Rows before:", len(sold), "| rows after:", len(clean), "| removed:", len(sold) - len(clean))
comparison = pd.DataFrame({
    "median_before": sold[fields].median(),
    "median_after": clean[fields].median(),
})
comparison["change_pct"] = (comparison["median_after"] / comparison["median_before"] - 1) * 100
print(comparison.round(2))