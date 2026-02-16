# Backend → Frontend API Response Reference

**Document Type:** Frontend Handoff — Build Reference  
**Version:** 1.0  
**Project:** SolarSense AI — Team 58  
**Audience:** Frontend developers with no prior knowledge of the DSE codebase  

---

## Important: Supported Energy Scenarios

The API supports **exactly two scenarios**. Frontend UI options must be constrained accordingly.

| Frontend UI Option | Supported? | How to Handle |
|-------------------|-----------|---------------|
| Fully on grid | ✅ Yes | Send `uses_diesel: false` |
| Off-grid with diesel generator | ✅ Yes | Send `uses_diesel: true` with diesel hours/price |
| Intermittent grid (no diesel) | ❌ Not modelled | Hide or disable this option; no DSE backing |
| Fully off-grid (no diesel) | ❌ Not modelled | Hide or disable; ROI math requires a grid tariff |
| Hybrid (solar + battery + grid + diesel) | ❌ Not modelled | Out of scope for v1 |
| Intermittent grid + diesel | ⚠️ Proxy only | Can use diesel_replacement path as a proxy — make clear to user it is approximate |

**If the frontend currently shows an intermittent-grid-only option, that option has no model backing and should not be presented as a supported input path in v1.**

---

## What You Are Receiving

When a user completes the SolarSense assessment form, backend calls a single endpoint and receives a single JSON object back. That JSON object is passed directly to frontend. **You do not call individual model endpoints** — you receive one fully assembled response from backend.

The response covers everything the UI needs:
- Estimated monthly energy consumption
- Predicted solar generation (scaled to this specific business)
- Recommended panel size and system cost
- ROI and monthly savings
- A viability verdict with score and explanation
- The user's current energy baseline costs
- (If the business uses diesel) Diesel economics details
- A 25-year generation projection suitable for charting

**Assessment endpoint (called by backend, not frontend directly):**
```
POST /api/v1/analyze
```

---

## The Complete Response Object

Below is the full annotated schema for every possible field. Optional fields are marked — they appear only in the diesel scenario.

---

### Section 1 — Business Identity Fields

These echo the user's input. Use them to personalise the results screen.

| Field Name | Type | Example Value | UI Usage | Chart? |
|------------|------|--------------|----------|--------|
| `business_name` | string | `"Joe's Coffee Shop"` | Results page header: *"Solar Assessment for Joe's Coffee Shop"* | No |
| `business_type` | string | `"Cafe"` | Sub-header or badge on results page | No |
| `location` | string | `"Nairobi, Kenya"` | Location label on results page | No |
| `analyzed_at` | string (ISO 8601) | `"2025-01-15T10:30:00.000000"` | "Assessment generated on 15 Jan 2025" footer label | No |

---

### Section 2 — Viability Verdict

These are the **primary outputs** — the first thing the user should see.

| Field Name | Type | Example Value | UI Usage | Chart? |
|------------|------|--------------|----------|--------|
| `status` | string | `"MODERATELY VIABLE"` | Large hero verdict card. Possible values: `"HIGHLY VIABLE"`, `"MODERATELY VIABLE"`, `"NOT VIABLE"`. Use as colour-coded badge (green / amber / red). | No |
| `recommendation` | string | `"Medium"` | Maps to status: `"High"` → Highly Viable, `"Medium"` → Moderately Viable, `"Low"` → Not Viable. Can drive icon or colour theming. | No |
| `viability_score` | float | `55.0` | Gauge/dial chart 0–100. Score ≥65 = green, 40–64 = amber, <40 = red. Label: *"Viability Score"*. | ✅ Gauge chart (0–100 scale) |
| `explanation` | string | `"Solar is moderately viable because: Moderate ROI of 18.0%; Good solar coverage (90%)."` | Plain text paragraph beneath the verdict card. Human-readable, no further formatting needed. | No |
| `confidence` | float | `85.0` | Shown as a percentage: *"Confidence: 85%"*. Tooltip: *"Based on completeness of your inputs."* | No |

**Viability score thresholds (for colour/icon logic):**

| Score Range | `status` Value | Suggested Colour |
|-------------|---------------|-----------------|
| 65–100 | `"HIGHLY VIABLE"` | Green (#22C55E or similar) |
| 40–64 | `"MODERATELY VIABLE"` | Amber (#F59E0B or similar) |
| 0–39 | `"NOT VIABLE"` | Red (#EF4444 or similar) |

---

### Section 3 — Energy & Solar Core Metrics

These four fields form the main metric cards below the verdict.

| Field Name | Type | Example Value | UI Usage | Chart? |
|------------|------|--------------|----------|--------|
| `estimated_consumption_kwh` | float | `450.0` | Metric card: *"Monthly Energy Use — 450 kWh"*. Subtitle: *"Estimated for your business"* | No — single metric card |
| `predicted_generation_kwh` | float | `405.0` | Metric card: *"Expected Solar Generation — 405 kWh/month"*. This is already sized to your business (not a generic 10m² figure). | No — single metric card |
| `recommended_panel_area_m2` | float | `10.0` | Metric card: *"Recommended Panel Size — 10 m²"*. Range will be 10–50m². | No — single metric card |
| `system_cost` | float | `6000.0` | Metric card: *"Estimated System Cost — $6,000"*. Basis: $600/m². | No — single metric card |

**Coverage ratio** (derive on frontend, not provided by API):
```javascript
const coveragePercent = ((predicted_generation_kwh / estimated_consumption_kwh) * 100).toFixed(0);
// Example: "90% of your energy needs covered"
```
Show as a progress bar or ring chart labelled *"Solar Coverage"*.

---

### Section 4 — Financial Returns

| Field Name | Type | Example Value | UI Usage | Chart? |
|------------|------|--------------|----------|--------|
| `monthly_savings` | float | `90.0` | Metric card: *"Monthly Savings — $90"*. Highlight this prominently as a key ROI proof point. | No — single metric card |
| `roi_percentage` | float | `18.0` | Metric card or badge: *"Return on Investment — 18%"*. Clamped 0–100% by the model. | No — single metric card |

**Annual savings** (derive on frontend):
```javascript
const annualSavings = (monthly_savings * 12).toFixed(2);
// "Annual savings: $1,080"
```

---

### Section 5 — Current Energy Baseline

These fields show what the user currently pays, providing context for the savings calculation.

| Field Name | Type | Example Value | UI Usage | Chart? |
|------------|------|--------------|----------|--------|
| `energy_scenario` | string | `"grid_only"` | Controls which baseline breakdown to display. Values: `"grid_only"` or `"diesel_replacement"`. | No |
| `current_energy_cost.total_monthly` | float | `67.50` | *"Your current monthly energy bill: $67.50"*. Use as baseline in before/after savings comparison. | ✅ Can be used in before/after bar chart |
| `current_energy_cost.grid_monthly` | float | `67.50` | Grid portion of baseline. In grid-only scenario this equals `total_monthly`. | ✅ Stacked bar (grid vs diesel) |
| `current_energy_cost.diesel_monthly` | float | `0.0` | Diesel portion of baseline. Zero in grid-only scenario. | ✅ Stacked bar (grid vs diesel) |

**Suggested before/after comparison chart:**  
Bar 1 = `current_energy_cost.total_monthly` (current cost)  
Bar 2 = `current_energy_cost.total_monthly - monthly_savings` (cost after solar)  
Label: *"Monthly Cost Before vs After Solar"*

---

### Section 5.5 — 25-Year Lifetime Generation (Time Series)

This data is now included directly in the `/analyze` response. You do not need a separate API call.

| Field Name | Type | Example Value | UI Usage | Chart? |
|------------|------|--------------|----------|--------|
| `lifetime_prediction.year_1_generation_kwh` | float | `1898.0` | *"Year 1 generation: 1,898 kWh"* — use as baseline in lifetime summary card | No — metric |
| `lifetime_prediction.lifetime_total_kwh` | float | `39250.0` | *"Total generation over 25 years: 39,250 kWh"* — headline summary | No — metric |
| `lifetime_prediction.lifetime_average_annual_kwh` | float | `1570.0` | *"Average annual generation: 1,570 kWh"* | No — metric |
| `lifetime_prediction.yearly_breakdown` | array (25 objects) | See below | Primary data for the 25-year line chart | ✅ Line chart — time series |
| `lifetime_prediction.yearly_breakdown[].year` | integer | `1` | X-axis value (Year 1 through 25) | ✅ X-axis |
| `lifetime_prediction.yearly_breakdown[].generation_kwh` | float | `1898.0` | Main line — annual generation | ✅ Main line |
| `lifetime_prediction.yearly_breakdown[].confidence_low_kwh` | float | `1708.2` | Lower shaded band | ✅ Area/band |
| `lifetime_prediction.yearly_breakdown[].confidence_high_kwh` | float | `2087.8` | Upper shaded band | ✅ Area/band |
| `lifetime_prediction.yearly_breakdown[].efficiency_pct` | float | `100.0` | Secondary axis or tooltip: *"Panel efficiency: 100%"* | ✅ Optional secondary axis |
| `lifetime_prediction.yearly_breakdown[].confidence_band_pct` | float | `10.0` | Tooltip label: *"±10% confidence range"* | No — tooltip only |
| `lifetime_prediction.monthly_generation_climatology` | array (12 objects) | See below | Monthly seasonal bar chart | ✅ Bar chart |
| `lifetime_prediction.monthly_generation_climatology[].month` | integer | `6` | X-axis (1–12, map to Jan–Dec) | ✅ X-axis |
| `lifetime_prediction.monthly_generation_climatology[].daily_kwh` | float | `5.2` | Bar height — daily generation for that month | ✅ Bar height |
| `lifetime_prediction.monthly_generation_climatology[].is_dry_season` | boolean | `true` | Use to colour-code bars: dry season = orange, wet season = blue | ✅ Bar colour |
| `lifetime_prediction.assumptions.annual_degradation_pct` | float | `0.7` | Tooltip/footnote: *"Assumes 0.7% annual panel degradation"* | No — footnote |
| `lifetime_prediction.confidence.years_1_5_band_pct` | float | `10.0` | Confidence legend label for years 1–5 | No — legend |
| `lifetime_prediction.confidence.years_6_15_band_pct` | float | `15.0` | Confidence legend label for years 6–15 | No — legend |
| `lifetime_prediction.confidence.years_16_25_band_pct` | float | `20.0` | Confidence legend label for years 16–25 | No — legend |

**25-year chart data access pattern:**
```javascript
const chartData = data.lifetime_prediction.yearly_breakdown.map(entry => ({
  year: entry.year,
  generation: entry.generation_kwh,
  low: entry.confidence_low_kwh,
  high: entry.confidence_high_kwh,
  efficiency: entry.efficiency_pct
}));
// Use in a line chart with shaded confidence band between low and high
```

**Monthly seasonality chart data:**
```javascript
const monthNames = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const seasonalData = data.lifetime_prediction.monthly_generation_climatology.map(m => ({
  month: monthNames[m.month - 1],
  dailyKwh: m.daily_kwh,
  isDrySeason: m.is_dry_season,
  colour: m.is_dry_season ? "#F59E0B" : "#3B82F6"
}));
```

---

**These fields only appear in the response when `energy_scenario === "diesel_replacement"`.**  
Do not attempt to render this section if the object is absent.

```javascript
if (data.energy_scenario === "diesel_replacement" && data.diesel_details) {
  // render diesel breakdown section
}
```

| Field Name | Type | Example Value | UI Usage | Chart? |
|------------|------|--------------|----------|--------|
| `diesel_details.hours_per_day` | float | `18` | *"Generator currently runs 18 hours/day"* | No |
| `diesel_details.price_per_liter` | float | `1.35` | *"Diesel price: $1.35/litre"* | No |
| `diesel_details.monthly_liters` | float | `194.4` | *"Monthly diesel consumption: 194 litres"* | No |
| `diesel_details.effective_tariff` | float | `0.63` | *"True cost of diesel power: $0.63/kWh"*. Useful for showing how much more expensive diesel is vs grid. | No |
| `diesel_details.diesel_kwh_monthly` | float | `337.5` | kWh generated by diesel per month. Use in energy source breakdown chart. | ✅ Pie/donut: diesel vs grid share |

**Suggested diesel breakdown visualisation:**  
Donut chart: diesel kWh (`diesel_details.diesel_kwh_monthly`) vs grid kWh (`current_energy_cost.grid_monthly / tariff`), labelled *"Your Current Energy Sources"*.

---

### Section 7 — Full Response Objects with All Fields

#### Grid-Only Example (full object)

```json
{
  "business_name": "Joe's Coffee Shop",
  "business_type": "Cafe",
  "location": "Nairobi, Kenya",
  "analyzed_at": "2025-01-15T10:30:00.000000",

  "status": "MODERATELY VIABLE",
  "recommendation": "Medium",
  "viability_score": 55.0,
  "explanation": "Solar is moderately viable because: Moderate ROI of 18.0%; Good solar coverage (90%).",
  "confidence": 85.0,

  "estimated_consumption_kwh": 450.0,
  "predicted_generation_kwh": 405.0,
  "recommended_panel_area_m2": 10.0,
  "system_cost": 6000.0,

  "monthly_savings": 90.0,
  "roi_percentage": 18.0,

  "energy_scenario": "grid_only",
  "current_energy_cost": {
    "total_monthly": 67.50,
    "diesel_monthly": 0.0,
    "grid_monthly": 67.50
  },

  "lifetime_prediction": {
    "year_1_generation_kwh": 1898.0,
    "lifetime_total_kwh": 39250.0,
    "lifetime_average_annual_kwh": 1570.0,
    "yearly_breakdown": [
      {
        "year": 1, "generation_kwh": 1898.0, "efficiency_pct": 100.0,
        "confidence_low_kwh": 1708.2, "confidence_high_kwh": 2087.8, "confidence_band_pct": 10.0
      },
      {
        "year": 2, "generation_kwh": 1884.7, "efficiency_pct": 99.3,
        "confidence_low_kwh": 1696.2, "confidence_high_kwh": 2073.2, "confidence_band_pct": 10.0
      }
    ],
    "assumptions": {
      "panel_area_m2": 10.0,
      "panel_efficiency_pct": 20.0,
      "lifetime_years": 25,
      "annual_degradation_pct": 0.7,
      "dry_months": [1, 2, 6, 7, 8, 12]
    },
    "confidence": {
      "year_1_band_pct": 10.0,
      "years_1_5_band_pct": 10.0,
      "years_6_15_band_pct": 15.0,
      "years_16_25_band_pct": 20.0
    },
    "monthly_generation_climatology": [
      { "month": 1, "daily_kwh": 5.1, "is_dry_season": true },
      { "month": 2, "daily_kwh": 4.9, "is_dry_season": true },
      { "month": 3, "daily_kwh": 4.8, "is_dry_season": false },
      { "month": 4, "daily_kwh": 4.5, "is_dry_season": false },
      { "month": 5, "daily_kwh": 4.3, "is_dry_season": false },
      { "month": 6, "daily_kwh": 5.2, "is_dry_season": true },
      { "month": 7, "daily_kwh": 5.4, "is_dry_season": true },
      { "month": 8, "daily_kwh": 5.3, "is_dry_season": true },
      { "month": 9, "daily_kwh": 4.6, "is_dry_season": false },
      { "month": 10, "daily_kwh": 4.4, "is_dry_season": false },
      { "month": 11, "daily_kwh": 4.7, "is_dry_season": false },
      { "month": 12, "daily_kwh": 5.0, "is_dry_season": true }
    ]
  }
}
```

Note: `diesel_details` is **absent** in the grid-only response. Do not expect or attempt to read it.

#### Diesel Replacement Example (full object)

```json
{
  "business_name": "Mombasa Cold Storage",
  "business_type": "Retail",
  "location": "Mombasa, Kenya",
  "analyzed_at": "2025-01-15T10:30:00.000000",

  "status": "HIGHLY VIABLE",
  "recommendation": "High",
  "viability_score": 78.2,
  "explanation": "Solar is highly viable because: Strong ROI of 34.5%; Excellent solar coverage (90%).; Significant savings ($285/mo).",
  "confidence": 85.0,

  "estimated_consumption_kwh": 756.0,
  "predicted_generation_kwh": 680.4,
  "recommended_panel_area_m2": 30.0,
  "system_cost": 18000.0,

  "monthly_savings": 285.0,
  "roi_percentage": 34.5,

  "energy_scenario": "diesel_replacement",
  "current_energy_cost": {
    "total_monthly": 492.0,
    "diesel_monthly": 356.0,
    "grid_monthly": 136.0
  },
  "diesel_details": {
    "hours_per_day": 18,
    "price_per_liter": 1.35,
    "monthly_liters": 194.4,
    "effective_tariff": 0.63,
    "diesel_kwh_monthly": 378.0
  }
}
```

---

### Section 8 — Chart & Visualisation Reference

This section maps every charting opportunity to the specific fields that feed it.

#### Chart 1 — Viability Gauge (Hero Section)
- **Type:** Gauge / dial, 0–100 range  
- **Data field:** `viability_score`  
- **Colour zones:** 0–39 = red, 40–64 = amber, 65–100 = green  
- **Label:** *"Viability Score: [viability_score]/100"*

#### Chart 2 — Energy Coverage Ring/Progress Bar
- **Type:** Ring chart or horizontal progress bar  
- **Data:** Derive `(predicted_generation_kwh / estimated_consumption_kwh) * 100`  
- **Label:** *"[coverage]% of your energy needs covered by solar"*

#### Chart 3 — Monthly Cost: Before vs After Solar
- **Type:** Grouped or side-by-side bar chart  
- **Bar A:** `current_energy_cost.total_monthly` — *"Current Monthly Cost"*  
- **Bar B:** `current_energy_cost.total_monthly - monthly_savings` — *"Monthly Cost with Solar"*  
- **Annotation:** `"Save $[monthly_savings]/month"`

#### Chart 4 — Current Energy Source Breakdown (Diesel Scenario Only)
- **Type:** Donut or pie chart  
- **Only render if:** `energy_scenario === "diesel_replacement"`  
- **Segment A:** `diesel_details.diesel_kwh_monthly` — *"Diesel Generator"*  
- **Segment B:** `current_energy_cost.grid_monthly / tariff` (or `estimated_consumption_kwh - diesel_details.diesel_kwh_monthly`) — *"Grid"*  
- **Title:** *"Your Current Energy Sources"*

#### Chart 5 — 25-Year Generation Projection (Time Series with Confidence Band)
- **Type:** Line chart with shaded confidence band
- **Data source:** `lifetime_prediction.yearly_breakdown` (25 entries)
- **X-axis:** `yearly_breakdown[].year` (1–25)
- **Main line:** `yearly_breakdown[].generation_kwh`
- **Shaded band:** between `yearly_breakdown[].confidence_low_kwh` and `yearly_breakdown[].confidence_high_kwh`
- **Footnote:** *"Assumes 0.7% annual panel degradation. Confidence bands widen over time: ±10% years 1–5, ±15% years 6–15, ±20% years 16–25."*
- **Note:** This data is now included in the `/analyze` response — no separate API call is needed.

#### Chart 6 — Monthly Solar Seasonality Bar Chart
- **Type:** Vertical bar chart, 12 bars
- **Data source:** `lifetime_prediction.monthly_generation_climatology`
- **X-axis:** Month name (map `month` index 1–12 to Jan–Dec)
- **Y-axis:** `daily_kwh` (typical daily generation)
- **Colour coding:** `is_dry_season: true` → amber/orange; `is_dry_season: false` → blue
- **Title:** *"Typical Daily Solar Generation by Month"*

---

### Section 9 — Error State

If analysis failed (e.g., one model was unavailable), backend will return HTTP 503 with:

```json
{
  "error": "Service Unavailable",
  "message": "Unable to complete analysis",
  "business_name": "Joe's Coffee Shop",
  "status": "INCOMPLETE"
}
```

**Frontend handling:**  
Check for `status === "INCOMPLETE"` or a non-200 HTTP status. Show a friendly error state:  
*"We weren't able to complete your assessment. Please try again in a moment."*

---

### Section 10 — Field Formatting Guidelines

| Field | Formatting Recommendation |
|-------|--------------------------|
| `estimated_consumption_kwh` | Round to nearest whole number: `Math.round(value)` |
| `predicted_generation_kwh` | Round to nearest whole number |
| `monthly_savings` | Two decimal places with USD symbol: `$90.00` |
| `roi_percentage` | One decimal place with % symbol: `18.0%` |
| `viability_score` | One decimal place, no unit: `55.0 / 100` |
| `confidence` | Round to nearest whole number with %: `85%` |
| `system_cost` | Formatted currency, no decimals for large numbers: `$6,000` |
| `recommended_panel_area_m2` | One decimal place with unit: `10.0 m²` |
| `current_energy_cost.*` | Two decimal places with USD symbol |
| `diesel_details.monthly_liters` | Round to nearest whole number: `194 litres` |
| `diesel_details.effective_tariff` | Two decimal places: `$0.63/kWh` |
| `analyzed_at` | Parse ISO 8601 and display as local date: `"15 Jan 2025"` |

---

### Section 11 — Fields That Do NOT Exist (Important)

The following fields are **not** in the response and must not be referenced or displayed. They were explicitly removed from the project scope:

| Field You Might Expect | Why It's Absent |
|------------------------|----------------|
| `payback_period_years` | Explicitly descoped — removed from all models |
| Any vendor or installer name | Platform is vendor-agnostic |
| Live meter readings | Pre-investment tool only; no live data |

Note: The 25-year lifetime projection **is** now included in `lifetime_prediction` — no separate API call is needed.

---

### Section 12 — Complete Field Index

Quick reference of every field in the `/analyze` response.

| # | Field Path | Type | Always Present? |
|---|-----------|------|----------------|
| 1 | `business_name` | string | ✅ Yes |
| 2 | `business_type` | string | ✅ Yes |
| 3 | `location` | string | ✅ Yes |
| 4 | `analyzed_at` | string | ✅ Yes |
| 5 | `status` | string | ✅ Yes |
| 6 | `recommendation` | string | ✅ Yes |
| 7 | `viability_score` | float | ✅ Yes |
| 8 | `explanation` | string | ✅ Yes |
| 9 | `confidence` | float | ✅ Yes |
| 10 | `estimated_consumption_kwh` | float | ✅ Yes |
| 11 | `predicted_generation_kwh` | float | ✅ Yes |
| 12 | `recommended_panel_area_m2` | float | ✅ Yes |
| 13 | `system_cost` | float | ✅ Yes |
| 14 | `monthly_savings` | float | ✅ Yes |
| 15 | `roi_percentage` | float | ✅ Yes |
| 16 | `energy_scenario` | string | ✅ Yes |
| 17 | `current_energy_cost.total_monthly` | float | ✅ Yes |
| 18 | `current_energy_cost.diesel_monthly` | float | ✅ Yes |
| 19 | `current_energy_cost.grid_monthly` | float | ✅ Yes |
| 20 | `lifetime_prediction.year_1_generation_kwh` | float | ✅ Yes |
| 21 | `lifetime_prediction.lifetime_total_kwh` | float | ✅ Yes |
| 22 | `lifetime_prediction.lifetime_average_annual_kwh` | float | ✅ Yes |
| 23 | `lifetime_prediction.yearly_breakdown` | array (25 objects) | ✅ Yes |
| 24 | `lifetime_prediction.yearly_breakdown[].year` | integer | ✅ Yes |
| 25 | `lifetime_prediction.yearly_breakdown[].generation_kwh` | float | ✅ Yes |
| 26 | `lifetime_prediction.yearly_breakdown[].efficiency_pct` | float | ✅ Yes |
| 27 | `lifetime_prediction.yearly_breakdown[].confidence_low_kwh` | float | ✅ Yes |
| 28 | `lifetime_prediction.yearly_breakdown[].confidence_high_kwh` | float | ✅ Yes |
| 29 | `lifetime_prediction.yearly_breakdown[].confidence_band_pct` | float | ✅ Yes |
| 30 | `lifetime_prediction.monthly_generation_climatology` | array (12 objects) | ✅ Yes |
| 31 | `lifetime_prediction.monthly_generation_climatology[].month` | integer | ✅ Yes |
| 32 | `lifetime_prediction.monthly_generation_climatology[].daily_kwh` | float | ✅ Yes |
| 33 | `lifetime_prediction.monthly_generation_climatology[].is_dry_season` | boolean | ✅ Yes |
| 34 | `lifetime_prediction.assumptions.annual_degradation_pct` | float | ✅ Yes |
| 35 | `lifetime_prediction.confidence.years_1_5_band_pct` | float | ✅ Yes |
| 36 | `lifetime_prediction.confidence.years_6_15_band_pct` | float | ✅ Yes |
| 37 | `lifetime_prediction.confidence.years_16_25_band_pct` | float | ✅ Yes |
| 38 | `diesel_details.hours_per_day` | float | ⚠️ Diesel only |
| 39 | `diesel_details.price_per_liter` | float | ⚠️ Diesel only |
| 40 | `diesel_details.monthly_liters` | float | ⚠️ Diesel only |
| 41 | `diesel_details.effective_tariff` | float | ⚠️ Diesel only |
| 42 | `diesel_details.diesel_kwh_monthly` | float | ⚠️ Diesel only |
