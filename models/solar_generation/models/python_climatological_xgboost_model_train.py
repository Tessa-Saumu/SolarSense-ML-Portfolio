# %% [markdown]
# # Model 2 (Climatological): Location-Aware Solar Viability – XGBoost
# 
# **Purpose**: Train a *climatological* XGBoost regression model that predicts **typical solar generation** from spatial–seasonal features (latitude, longitude, month, dry-season flag) using monthly-aggregated NASA POWER data.
# 
# **Key Differences vs. Daily Baseline (02-baseline-model-xgboost):**
# - Focuses on **monthly averages** (climatology), not noisy daily weather.
# - Target is **typical expected daily generation** for a 10m², 20%-efficiency system.
# - Training/validation split is by **location**, to test generalisation to unseen cities.
# 
# **Target Metric**: MAPE ≤ 15% on held-out *locations* (goal 8–12%).
# 
# This notebook mirrors the baseline notebook style but uses the redesigned climatological problem framing aligned with the DSE brief.
# 

# %%
# Imports & configuration

import pandas as pd
import numpy as np
from pathlib import Path
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_percentage_error
import matplotlib
matplotlib.use('Agg')  # no display needed when running as script
import matplotlib.pyplot as plt
import seaborn as sns

# Define these directly — no service module needed
DRY_MONTHS = {12, 1, 2, 6, 7, 8}
FEATURE_COLUMNS = ["latitude", "longitude", "abs_latitude", "month", "is_dry_season"]

DATA_CSV_PATH = Path(r"C:\Users\ingex\OneDrive\Documents\Git Projects\SolarSense AI ML Microservice\Model-1-branch\models\solar_generation\notebooks\solar_data_20cities_4yr.csv")
# DATA_CSV_PATH = Path(r"C:\Users\ingex\OneDrive\Documents\Git Projects\SolarSense AI ML Microservice\Model-1-branch\models\solar_generation\models\python_climatological_xgboost_model_train.py")
MODEL_TYPE = "XGBoost climatological regression"


# %%
# 1. Load merged NASA POWER dataset

if not DATA_CSV_PATH.exists():
    raise FileNotFoundError(
        f"Expected merged solar data CSV at '{DATA_CSV_PATH}', "
        "but it was not found. Run the Nasa_pipeline + cleaning first."
    )

raw_df = pd.read_csv(DATA_CSV_PATH)
print(f"Loaded {len(raw_df):,} daily records from {DATA_CSV_PATH}")
print("Columns:", raw_df.columns.tolist())

# Use only high-quality records
raw_df = raw_df[raw_df["data_quality"] == "good"].copy()
print(f"After quality filter: {len(raw_df):,} records")

raw_df["date"] = pd.to_datetime(raw_df["date"])
raw_df["month"] = raw_df["date"].dt.month

print(raw_df.head())

# %%
# 2. Aggregate to monthly climatology per city

monthly = (
    raw_df.groupby([
        "location_name",
        "country",
        "latitude",
        "longitude",
        "month",
    ], as_index=False)["ghi_kwh_m2"]
    .mean()
    .rename(columns={"ghi_kwh_m2": "avg_ghi_kwh_m2"})
)

# Spatial + seasonal features
monthly["abs_latitude"] = monthly["latitude"].abs()
monthly["is_dry_season"] = monthly["month"].isin(DRY_MONTHS).astype(int)

# Target: typical expected generation for 10m², 20% efficiency
monthly["target_avg_generation_kwh"] = monthly["avg_ghi_kwh_m2"] * 10.0 * 0.2

print(f"Monthly climatology rows: {len(monthly)}")
print("Locations:", sorted(monthly["location_name"].unique()))
print(monthly.head())


# %%
# 3. Visualise monthly GHI patterns by location

fig, ax = plt.subplots(figsize=(10, 6))

sns.lineplot(
    data=monthly,
    x="month",
    y="avg_ghi_kwh_m2",
    hue="location_name",
    marker="o",
    ax=ax,
)

ax.set_title("Monthly Climatological GHI by Location (NASA POWER)")
ax.set_xlabel("Month")
ax.set_ylabel("Avg GHI (kWh/m²/day)")
ax.legend(title="Location", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.show()


# %%
# 4. Train/validation split by LOCATION (spatial generalisation)

all_locations = sorted(monthly["location_name"].unique())
print("All locations:", all_locations)

# Prefer to hold out a mix of climates for validation
preferred_val = ["Johannesburg_SA", "Cape_Town_SA", "Abidjan_Ivory_Coast", "Lusaka_Zambia"]
val_locations = [loc for loc in preferred_val if loc in all_locations]

if not val_locations:
    # Fallback: last 2 alphabetically
    val_locations = all_locations[-2:]

print("\nTrain locations vs Validation locations:")
print("Validation:", val_locations)
train_locations = [loc for loc in all_locations if loc not in val_locations]
print("Train:", train_locations)

train_df = monthly[monthly["location_name"].isin(train_locations)].reset_index(drop=True)
val_df = monthly[monthly["location_name"].isin(val_locations)].reset_index(drop=True)

X_train = train_df[FEATURE_COLUMNS]
y_train = train_df["target_avg_generation_kwh"]

X_val = val_df[FEATURE_COLUMNS]
y_val = val_df["target_avg_generation_kwh"]

print(train_df.head())


# %%
# 5. Train XGBoost climatological regression model

model = XGBRegressor(
    n_estimators=400,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.9,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1,
)

model.fit(X_train, y_train)

y_val_pred = model.predict(X_val)

mape = mean_absolute_percentage_error(y_val, y_val_pred)
print(f"Validation MAPE (location-based): {mape * 100:.2f}%")

# Enforce DSE acceptance criterion
assert mape <= 0.15, f"MAPE {mape * 100:.2f}% exceeds 15% threshold"


# %%
# 6. Visual diagnostics – predictions vs actuals, by location

val_results = val_df.copy()
val_results["y_true"] = y_val
val_results["y_pred"] = y_val_pred
val_results["abs_pct_error"] = (val_results["y_pred"] - val_results["y_true"]).abs() / val_results["y_true"]

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# (a) Scatter: true vs predicted
sns.scatterplot(
    data=val_results,
    x="y_true",
    y="y_pred",
    hue="location_name",
    ax=axes[0],
)
axes[0].plot(
    [val_results["y_true"].min(), val_results["y_true"].max()],
    [val_results["y_true"].min(), val_results["y_true"].max()],
    ls="--",
    color="black",
)
axes[0].set_xlabel("True avg generation (kWh/day)")
axes[0].set_ylabel("Predicted avg generation (kWh/day)")
axes[0].set_title("Validation: True vs Predicted (by location)")

# (b) Bar: MAPE by validation location
mape_by_loc = (
    val_results.groupby("location_name")["abs_pct_error"].mean().reset_index()
)

sns.barplot(
    data=mape_by_loc,
    x="location_name",
    y="abs_pct_error",
    ax=axes[1],
)
axes[1].set_ylabel("MAPE (fraction)")
axes[1].set_xlabel("")
axes[1].set_title("Location-wise MAPE on held-out cities")
axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=45, ha="right")

plt.tight_layout()
plt.show()

mape_by_loc

# %%
# 7. Feature importance (why this is ML, not a lookup table)

from xgboost import plot_importance

fig, ax = plt.subplots(figsize=(8, 5))
plot_importance(model, ax=ax)
ax.set_title("XGBoost Feature Importance – Climatological Model")
plt.tight_layout()
plt.show()

list(zip(FEATURE_COLUMNS, model.feature_importances_))

# %%
# 8. Save model artifacts directly — no service module dependency

import os, json, joblib
from pathlib import Path
from datetime import datetime

# ── Set this to wherever you want the API to load from ──
SAVE_DIR = Path(r"C:\Users\ingex\OneDrive\Documents\Git Projects\SolarSense AI ML Microservice\Model-1-branch\models\solar_generation\models")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

# Save model using XGBoost native format (version-safe)
model.save_model(str(SAVE_DIR / "xgboost_climatological_model_v2.json"))

# Save feature columns
joblib.dump(FEATURE_COLUMNS, SAVE_DIR / "feature_columns_v2.pkl")

# Save metadata
metadata = {
    "model_type": "XGBoost climatological regression",
    "created_at_utc": datetime.utcnow().isoformat() + "Z",
    "validation_mape": float(mape),
    "training_locations": sorted(monthly["location_name"].unique().tolist()),
    "feature_columns": FEATURE_COLUMNS,
}
(SAVE_DIR / "xgboost_climatological_metadata_v2.json").write_text(json.dumps(metadata, indent=2))

# Verify immediately
import numpy as np
from xgboost import XGBRegressor
m_check = XGBRegressor()
m_check.load_model(str(SAVE_DIR / "xgboost_climatological_model_v2.json"))
X_test = np.array([[-1.2921, 36.8219, 1.2921, 2, 1]])
print("Nairobi Feb check:", m_check.predict(X_test))  # should be ~11.67
print("Saved to:", SAVE_DIR)

# %%
# 9. Per-location validation over all cities (bar chart + PNG)

from pathlib import Path as _Path

outputs_dir = _Path("outputs")
outputs_dir.mkdir(exist_ok=True)

per_loc_results = []

for loc in sorted(monthly["location_name"].unique()):
    df_loc = monthly[monthly["location_name"] == loc]
    X_loc = df_loc[FEATURE_COLUMNS]
    y_loc = df_loc["target_avg_generation_kwh"]
    y_loc_pred = model.predict(X_loc)
    loc_mape = mean_absolute_percentage_error(y_loc, y_loc_pred)
    per_loc_results.append({"location_name": loc, "mape": loc_mape})

per_loc_df = pd.DataFrame(per_loc_results)
print(per_loc_df)

fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(data=per_loc_df, x="location_name", y="mape", ax=ax)
ax.set_ylabel("MAPE (fraction)")
ax.set_xlabel("")
ax.set_title("Per-location MAPE (all 20 cities)")
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
plt.tight_layout()

png_path = outputs_dir / "per_location_validation.png"
plt.savefig(png_path, dpi=150)
plt.show()

print(f"Saved per-location validation chart to {png_path}")


# %%
# 10. Demo: point prediction + lifetime projection helpers

# lat_demo, lon_demo, month_demo = -1.2921, 36.8219, 6  # Nairobi, June

# coord_check = validate_coordinates(lat_demo, lon_demo)
# print("Coordinate validation:", coord_check)

# pred_daily = predict_solar_generation(lat_demo, lon_demo, month_demo)
# print(f"Typical daily generation (month={month_demo}): {pred_daily:.2f} kWh/day")

# lifetime = predict_lifetime_generation(lat_demo, lon_demo, lifetime_years=25)
# print(
#     f"Year 1 generation: {lifetime['year_1_generation_kwh']:.0f} kWh, "
#     f"Lifetime total: {lifetime['lifetime_total_kwh']:.0f} kWh",
# )

# lifetime["year_1_generation_kwh"], lifetime["lifetime_total_kwh"], lifetime["lifetime_average_annual_kwh"]


# %%
import numpy as np
import xgboost as xgb

m = xgb.Booster()
m.load_model(r"models\solar_generation\models\xgboost_climatological_model_v2.json")

feature_names = ["latitude", "longitude", "abs_latitude", "month", "is_dry_season"]
X = np.array([[-1.89, 36.8219, -1.2921, 2, 1]])
dm = xgb.DMatrix(X, feature_names=feature_names)
print(m.predict(dm))


