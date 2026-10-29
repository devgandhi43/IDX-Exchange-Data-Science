import pandas as pd
#Sold:     rows before 495,321 | rows after 495,085
#Listings: rows before 625,325 | rows after 624,897
#Date flags (sold): listing_after_close 75 | purchase_after_close 242 | negative_timeline 315
#Date flags (listings): listing_after_close 88 | purchase_after_close 247 | negative_timeline 307
#Geographic (sold): missing coordinates 4,794 | latitude = 0 46 | longitude > 0 35 | outside California 116
#Geographic (listings): missing coordinates 74,236 | latitude = 0 92 | longitude > 0 94 | outside California 389

dates = ["CloseDate", "PurchaseContractDate", "ListingContractDate", "ContractStatusChangeDate"]
numbers = ["ClosePrice", "ListPrice", "OriginalListPrice", "LivingArea", "LotSizeAcres", "BedroomsTotal",
           "BathroomsTotalInteger", "DaysOnMarket", "YearBuilt", "Latitude", "Longitude"]
required = {"sold": ["ClosePrice", "CloseDate"], "listings": ["ListPrice", "ListingContractDate"]}
date_flags = ["listing_after_close_flag", "purchase_after_close_flag", "negative_timeline_flag"]
geo_flags = ["missing_coords_flag", "lat_zero_flag", "lon_positive_flag", "out_of_state_flag"]

for name in required:
    df = pd.read_csv("data/processed/" + name + "_with_rates.csv", low_memory=False)
    print("\n" + name.upper())
    print("Rows before:", len(df))

    for col in dates:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in numbers:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    print(df[dates + numbers].dtypes)

    nulls = df.isna().mean() * 100
    drop = [c for c in df.columns if c.endswith(".1") or (nulls[c] > 90 and c not in dates + numbers)]
    df = df.drop(columns=drop)
    print("Columns dropped:", len(drop))

    df = df.dropna(subset=required[name])

    bad = (df["ClosePrice"] <= 0) | (df["LivingArea"] <= 0) | (df["DaysOnMarket"] < 0) | (df["BedroomsTotal"] < 0) | (df["BathroomsTotalInteger"] < 0)
    print("Invalid rows removed:", bad.sum())
    df = df[~bad].copy()

    df["listing_after_close_flag"] = df["ListingContractDate"] > df["CloseDate"]
    df["purchase_after_close_flag"] = df["PurchaseContractDate"] > df["CloseDate"]
    df["negative_timeline_flag"] = df["ListingContractDate"] > df["PurchaseContractDate"]
    print(df[date_flags].sum())

    lat = df["Latitude"]
    lon = df["Longitude"]
    df["missing_coords_flag"] = lat.isna() | lon.isna()
    df["lat_zero_flag"] = lat == 0
    df["lon_positive_flag"] = lon > 0
    df["out_of_state_flag"] = lat.notna() & lon.notna() & ~(lat.between(32.5, 42) & lon.between(-124.5, -114))
    print(df[geo_flags].sum())

    print("Rows after:", len(df))
    df.to_csv("data/processed/" + name + "_clean.csv", index=False)