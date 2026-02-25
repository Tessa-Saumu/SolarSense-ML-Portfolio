# MODEL 4 TEST SUITE - DETAILED COMPARISON

**Test Date:** 2026-02-25T14:11:54.455099


## 1. Lagos Fresh Cuts Butchery

**Status:** ❌ FAIL

**Country:** Nigeria

### 📥 Input

- **Business Type:** Butchery
- **Location:** Lagos, Nigeria
- **Coordinates:** (6.5244, 3.3792)
- **Uses Diesel:** True
  - Hours/day: 8.0
  - Price/liter: $0.26
- **Equipment:** 3 items

### 📊 Comparison

| Metric | Expected | Actual | Deviation | Status |
|--------|----------|--------|-----------|--------|
| Consumption (kWh/mo) | 3200.0 | 320.1 | -90.0% | ❌ |
| System Cost (USD) | $2,555 | $8,625 | +237.6% | ❌ |
| System Cost (₦) | ₦3,960,000 | ₦13,368,750 | +237.6% | ❌ |
| Monthly Savings (USD) | $464.52 | $136.58 | -70.6% | ❌ |
| Monthly Savings (₦) | ₦720,000 | ₦211,699 | -70.6% | ❌ |
| Payback (years) | 0.5 | 5.3 | +952.5% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 63.67
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 19.0
- **Energy Scenario:** diesel_replacement

---

## 2. Accra Daily Grocery

**Status:** ❌ FAIL

**Country:** Ghana

### 📥 Input

- **Business Type:** Grocery
- **Location:** Accra, Ghana
- **Coordinates:** (5.6037, -0.187)
- **Uses Diesel:** False
- **Equipment:** 3 items

### 📊 Comparison

| Metric | Expected | Actual | Deviation | Status |
|--------|----------|--------|-----------|--------|
| Consumption (kWh/mo) | 2200.0 | 274.9 | -87.5% | ❌ |
| System Cost (USD) | $2,088 | $8,250 | +295.1% | ❌ |
| System Cost (GHS) | GHS26,100 | GHS103,125 | +295.1% | ❌ |
| Monthly Savings (USD) | $380.16 | $35.74 | -90.6% | ❌ |
| Monthly Savings (GHS) | GHS4,752 | GHS447 | -90.6% | ❌ |
| Payback (years) | 0.5 | 19.2 | +3747.2% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 45.3
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 5.2
- **Energy Scenario:** grid_only

---

## 3. Nairobi Bread Haven Bakery

**Status:** ❌ FAIL

**Country:** Kenya

### 📥 Input

- **Business Type:** Bakery
- **Location:** Nairobi, Kenya
- **Coordinates:** (-1.2921, 36.8219)
- **Uses Diesel:** True
  - Hours/day: 10.0
  - Price/liter: $1.50
- **Equipment:** 3 items

### 📊 Comparison

| Metric | Expected | Actual | Deviation | Status |
|--------|----------|--------|-----------|--------|
| Consumption (kWh/mo) | 2800.0 | 182.6 | -93.5% | ❌ |
| System Cost (USD) | $2,500 | $8,100 | +224.0% | ❌ |
| System Cost (KES) | KES350,000 | KES1,134,000 | +224.0% | ❌ |
| Monthly Savings (USD) | $905.36 | $207.35 | -77.1% | ❌ |
| Monthly Savings (KES) | KES126,750 | KES29,029 | -77.1% | ❌ |
| Payback (years) | 0.2 | 3.3 | +1527.7% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 74.2
- **Recommendation:** High
- **Status:** HIGHLY VIABLE
- **ROI %:** 30.72
- **Energy Scenario:** diesel_replacement

---

## 4. Johannesburg ChillMart Supermarket

**Status:** ❌ FAIL

**Country:** South Africa

### 📥 Input

- **Business Type:** Supermarket/mini mart
- **Location:** Johannesburg, South Africa
- **Coordinates:** (-26.2041, 28.0473)
- **Uses Diesel:** False
- **Equipment:** 3 items

### 📊 Comparison

| Metric | Expected | Actual | Deviation | Status |
|--------|----------|--------|-----------|--------|
| Consumption (kWh/mo) | 4500.0 | 629.0 | -86.0% | ❌ |
| System Cost (USD) | $4,832 | $10,331 | +113.8% | ❌ |
| System Cost (R) | R89,400 | R191,122 | +113.8% | ❌ |
| Monthly Savings (USD) | $634.86 | $79.25 | -87.5% | ❌ |
| Monthly Savings (R) | R11,745 | R1,466 | -87.5% | ❌ |
| Payback (years) | 0.6 | 10.9 | +1710.5% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 48.31
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 9.21
- **Energy Scenario:** grid_only

---

## 5. Addis Ice Foods Frozen Retail

**Status:** ❌ FAIL

**Country:** Ethiopia

### 📥 Input

- **Business Type:** Frozen food retail
- **Location:** Addis Ababa, Ethiopia
- **Coordinates:** (9.032, 38.7469)
- **Uses Diesel:** True
  - Hours/day: 6.0
  - Price/liter: $0.98
- **Equipment:** 2 items

### 📊 Comparison

| Metric | Expected | Actual | Deviation | Status |
|--------|----------|--------|-----------|--------|
| Consumption (kWh/mo) | 3800.0 | 302.2 | -92.0% | ❌ |
| System Cost (USD) | $2,732 | $8,400 | +207.5% | ❌ |
| System Cost (ETB) | ETB153,000 | ETB470,400 | +207.5% | ❌ |
| Monthly Savings (USD) | $491.52 | $133.29 | -72.9% | ❌ |
| Monthly Savings (ETB) | ETB27,525 | ETB7,464 | -72.9% | ❌ |
| Payback (years) | 0.5 | 5.3 | +950.3% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 66.06
- **Recommendation:** High
- **Status:** HIGHLY VIABLE
- **ROI %:** 19.04
- **Energy Scenario:** diesel_replacement

---

## 6. Kampala Farm Cold Storage

**Status:** ❌ FAIL

**Country:** Uganda

### 📥 Input

- **Business Type:** Cold storage
- **Location:** Kampala, Uganda
- **Coordinates:** (0.3476, 32.5825)
- **Uses Diesel:** False
- **Equipment:** 3 items

### 📊 Comparison

| Metric | Expected | Actual | Deviation | Status |
|--------|----------|--------|-----------|--------|
| Consumption (kWh/mo) | 4100.0 | 517.2 | -87.4% | ❌ |
| System Cost (USD) | $3,716 | $10,545 | +183.7% | ❌ |
| System Cost (UGX) | UGX13,750,000 | UGX39,014,761 | +183.7% | ❌ |
| Monthly Savings (USD) | $1195.95 | $51.21 | -95.7% | ❌ |
| Monthly Savings (UGX) | UGX4,425,000 | UGX189,477 | -95.7% | ❌ |
| Payback (years) | 0.3 | 17.2 | +5619.7% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 43.25
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 5.83
- **Energy Scenario:** grid_only

---

## 7. Kigali Quick Freeze Butchery

**Status:** ❌ FAIL

**Country:** Rwanda

### 📥 Input

- **Business Type:** Butchery
- **Location:** Kigali, Rwanda
- **Coordinates:** (-1.9536, 30.0606)
- **Uses Diesel:** True
  - Hours/day: 12.0
  - Price/liter: $1.15
- **Equipment:** 3 items

### 📊 Comparison

| Metric | Expected | Actual | Deviation | Status |
|--------|----------|--------|-----------|--------|
| Consumption (kWh/mo) | 2600.0 | 271.4 | -89.6% | ❌ |
| System Cost (USD) | $2,265 | $8,100 | +257.6% | ❌ |
| System Cost (RWF) | RWF2,945,000 | RWF10,530,000 | +257.6% | ❌ |
| Monthly Savings (USD) | $1125.00 | $257.55 | -77.1% | ❌ |
| Monthly Savings (RWF) | RWF1,462,500 | RWF334,815 | -77.1% | ❌ |
| Payback (years) | 0.2 | 2.6 | +1210.4% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 78.85
- **Recommendation:** High
- **Status:** HIGHLY VIABLE
- **ROI %:** 38.16
- **Energy Scenario:** diesel_replacement

---

## 8. Dar Fresh Mart Grocery

**Status:** ❌ FAIL

**Country:** Tanzania

### 📥 Input

- **Business Type:** Grocery
- **Location:** Dar es Salaam, Tanzania
- **Coordinates:** (-6.7924, 39.2083)
- **Uses Diesel:** False
- **Equipment:** 3 items

### 📊 Comparison

| Metric | Expected | Actual | Deviation | Status |
|--------|----------|--------|-----------|--------|
| Consumption (kWh/mo) | 2400.0 | 320.1 | -86.7% | ❌ |
| System Cost (USD) | $1,888 | $8,100 | +329.1% | ❌ |
| System Cost (TZS) | TZS4,436,000 | TZS19,035,000 | +329.1% | ❌ |
| Monthly Savings (USD) | $367.02 | $35.21 | -90.4% | ❌ |
| Monthly Savings (TZS) | TZS862,500 | TZS82,744 | -90.4% | ❌ |
| Payback (years) | 0.4 | 19.2 | +4692.7% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 45.33
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 5.22
- **Energy Scenario:** grid_only

---

## 9. Cape Meat Locker Cold Storage

**Status:** ❌ FAIL

**Country:** South Africa

### 📥 Input

- **Business Type:** Cold storage
- **Location:** Cape Town, South Africa
- **Coordinates:** (-33.9249, 18.4241)
- **Uses Diesel:** True
  - Hours/day: 5.0
  - Price/liter: $1.24
- **Equipment:** 2 items

### 📊 Comparison

| Metric | Expected | Actual | Deviation | Status |
|--------|----------|--------|-----------|--------|
| Consumption (kWh/mo) | 5200.0 | 815.5 | -84.3% | ❌ |
| System Cost (USD) | $5,573 | $12,775 | +129.2% | ❌ |
| System Cost (R) | R103,100 | R236,338 | +129.2% | ❌ |
| Monthly Savings (USD) | $956.76 | $224.89 | -76.5% | ❌ |
| Monthly Savings (R) | R17,700 | R4,160 | -76.5% | ❌ |
| Payback (years) | 0.5 | 4.7 | +846.8% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 65.21
- **Recommendation:** High
- **Status:** HIGHLY VIABLE
- **ROI %:** 21.13
- **Energy Scenario:** diesel_replacement

---

## 10. Nairobi Frosty Mini Mart

**Status:** ❌ FAIL

**Country:** Kenya

### 📥 Input

- **Business Type:** Supermarket/mini mart
- **Location:** Nairobi, Kenya
- **Coordinates:** (-1.2921, 36.8219)
- **Uses Diesel:** False
- **Equipment:** 4 items

### 📊 Comparison

| Metric | Expected | Actual | Deviation | Status |
|--------|----------|--------|-----------|--------|
| Consumption (kWh/mo) | 3600.0 | 601.9 | -83.3% | ❌ |
| System Cost (USD) | $3,543 | $11,618 | +227.9% | ❌ |
| System Cost (KES) | KES496,000 | KES1,626,493 | +227.9% | ❌ |
| Monthly Savings (USD) | $557.14 | $59.58 | -89.3% | ❌ |
| Monthly Savings (KES) | KES78,000 | KES8,341 | -89.3% | ❌ |
| Payback (years) | 0.5 | 16.2 | +3149.9% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 43.72
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 6.15
- **Energy Scenario:** grid_only

---
