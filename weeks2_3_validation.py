import glob
import pandas as pd
import os
import matplotlib.pyplot as plt
# ANSWERS
# Property types: Residential, ResidentialLease, Land, ResidentialIncome, ManufacturedInPark, CommercialSale, CommercialLease, BusinessOpportunity
# Keep rows PropertyType == Residential: sold: 495,321 rows; listings: 625,325 rows
# Columns over 90% null sold: TaxYear, FireplacesTotal, TaxAnnualAmount, AboveGradeFinishedArea, ElementarySchoolDistrict, BusinessType, CoveredSpaces, MiddleOrJuniorSchoolDistrict, WaterfrontYN, BelowGradeFinishedArea, BasementYN, BuilderName, LotSizeDimensions, BuildingAreaTotal, CoBuyerAgentFirstName
# Columns over 90% null listings: TaxYear, TaxAnnualAmount, AboveGradeFinishedArea, FireplacesTotal, ElementarySchoolDistrict, BusinessType, CoveredSpaces, MiddleOrJuniorSchoolDistrict, BelowGradeFinishedArea, CoBuyerAgentFirstName, BuilderName, LotSizeDimensions, BuyerAgencyCompensation, BuyerAgencyCompensationType, BuildingAreaTotal
# ClosePrice: min 0; max 989,500,000; mean 1,188,206.86; median 825,000
# LivingArea: min 0; max 17,021,321; mean 1,902.58; median 1,648
# DaysOnMarket: min -288; max 12,430; mean 37.64; median 19

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 50)
pd.set_option("display.float_format", "{:,.2f}".format)

files = sorted(glob.glob("data/raw/CRMLSSold2*.csv"))
types = pd.concat(pd.read_csv(f, usecols=["PropertyType"], encoding_errors="replace") for f in files)
print("Property types found:")
print(types["PropertyType"].value_counts(dropna=False))

for name in ["sold", "listings"]:
    df = pd.read_csv(f"data/processed/{name}_combined_residential.csv", low_memory=False)
    df = df[df["PropertyType"] == "Residential"]

    nulls = pd.DataFrame({"null_count": df.isna().sum(), "null_pct": df.isna().mean() * 100})
    nulls = nulls.sort_values("null_pct", ascending=False)

    print(f"\n{name}: {len(df):,} rows, {df.shape[1]} columns")
    print(nulls.head(25))
    print("Columns over 90% null:", list(nulls.index[nulls["null_pct"] > 90]))

    df.to_csv(f"data/processed/{name}_filtered.csv", index=False)
    if name == "sold":
        sold = df

fields = sold[["ClosePrice", "LivingArea", "DaysOnMarket"]].apply(pd.to_numeric, errors="coerce")
print("\nNumeric summary (sold):")
print(fields.describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]))
os.makedirs("figures", exist_ok=True)
for col in ["ClosePrice", "ListPrice", "OriginalListPrice", "LivingArea", "LotSizeAcres", "BedroomsTotal", "BathroomsTotalInteger", "DaysOnMarket", "YearBuilt"]:
    s = pd.to_numeric(sold[col], errors="coerce").dropna()
    s = s[(s >= s.quantile(0.01)) & (s <= s.quantile(0.99))]
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].hist(s, bins=50)
    ax[0].set_title(col + " histogram")
    ax[1].boxplot(s, vert=False)
    ax[1].set_title(col + " boxplot")
    fig.savefig(f"figures/{col}.png")
    plt.close(fig)