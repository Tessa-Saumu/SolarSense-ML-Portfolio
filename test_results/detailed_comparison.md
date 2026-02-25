# MODEL 4 TEST SUITE - DETAILED COMPARISON

**Test Date:** 2026-02-25T15:18:27.259030


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
| Consumption (kWh/mo) | 3200.0 | 6088.8 | +90.3% | ❌ |
| System Cost (USD) | $2,555 | $9,200 | +260.1% | ❌ |
| System Cost (₦) | ₦3,960,000 | ₦14,260,000 | +260.1% | ❌ |
| Monthly Savings (USD) | $464.52 | $158.60 | -65.9% | ❌ |
| Monthly Savings (₦) | ₦720,000 | ₦245,830 | -65.9% | ❌ |
| Payback (years) | 0.5 | 4.8 | +866.8% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 45.2
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 20.69
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
| Consumption (kWh/mo) | 2200.0 | 6147.2 | +179.4% | ❌ |
| System Cost (USD) | $2,088 | $8,800 | +321.5% | ❌ |
| System Cost (GHS) | GHS26,100 | GHS110,000 | +321.5% | ❌ |
| Monthly Savings (USD) | $380.16 | $197.02 | -48.2% | ❌ |
| Monthly Savings (GHS) | GHS4,752 | GHS2,463 | -48.2% | ❌ |
| Payback (years) | 0.5 | 3.7 | +644.4% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 49.19
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 26.87
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
| Consumption (kWh/mo) | 2800.0 | 4882.3 | +74.4% | ❌ |
| System Cost (USD) | $2,500 | $8,640 | +245.6% | ❌ |
| System Cost (KES) | KES350,000 | KES1,209,600 | +245.6% | ❌ |
| Monthly Savings (USD) | $905.36 | $603.74 | -33.3% | ❌ |
| Monthly Savings (KES) | KES126,750 | KES84,524 | -33.3% | ❌ |
| Payback (years) | 0.2 | 1.2 | +496.3% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 60.76
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 83.85
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
| Consumption (kWh/mo) | 4500.0 | 5497.2 | +22.2% | ⚠️ |
| System Cost (USD) | $4,832 | $7,200 | +49.0% | ❌ |
| System Cost (R) | R89,400 | R133,200 | +49.0% | ❌ |
| Monthly Savings (USD) | $634.86 | $235.28 | -62.9% | ❌ |
| Monthly Savings (R) | R11,745 | R4,353 | -62.9% | ❌ |
| Payback (years) | 0.6 | 2.6 | +325.0% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 58.68
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 39.21
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
| Consumption (kWh/mo) | 3800.0 | 3778.9 | -0.6% | ✅ |
| System Cost (USD) | $2,732 | $8,960 | +227.9% | ❌ |
| System Cost (ETB) | ETB153,000 | ETB501,760 | +227.9% | ❌ |
| Monthly Savings (USD) | $491.52 | $330.87 | -32.7% | ❌ |
| Monthly Savings (ETB) | ETB27,525 | ETB18,529 | -32.7% | ❌ |
| Payback (years) | 0.5 | 2.3 | +351.3% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 65.73
- **Recommendation:** High
- **Status:** HIGHLY VIABLE
- **ROI %:** 44.31
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
| Consumption (kWh/mo) | 4100.0 | 8253.9 | +101.3% | ❌ |
| System Cost (USD) | $3,716 | $8,640 | +132.5% | ❌ |
| System Cost (UGX) | UGX13,750,000 | UGX31,968,000 | +132.5% | ❌ |
| Monthly Savings (USD) | $1195.95 | $187.00 | -84.4% | ❌ |
| Monthly Savings (UGX) | UGX4,425,000 | UGX691,900 | -84.4% | ❌ |
| Payback (years) | 0.3 | 3.9 | +1183.4% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 47.41
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 25.97
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
| Consumption (kWh/mo) | 2600.0 | 3809.8 | +46.5% | ❌ |
| System Cost (USD) | $2,265 | $8,640 | +281.4% | ❌ |
| System Cost (RWF) | RWF2,945,000 | RWF11,232,000 | +281.4% | ❌ |
| Monthly Savings (USD) | $1125.00 | $518.10 | -53.9% | ❌ |
| Monthly Savings (RWF) | RWF1,462,500 | RWF673,530 | -53.9% | ❌ |
| Payback (years) | 0.2 | 1.4 | +594.8% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 62.25
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 71.96
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
| Consumption (kWh/mo) | 2400.0 | 6741.2 | +180.9% | ❌ |
| System Cost (USD) | $1,888 | $8,640 | +357.7% | ❌ |
| System Cost (TZS) | TZS4,436,000 | TZS20,304,000 | +357.7% | ❌ |
| Monthly Savings (USD) | $367.02 | $212.35 | -42.1% | ❌ |
| Monthly Savings (TZS) | TZS862,500 | TZS499,022 | -42.1% | ❌ |
| Payback (years) | 0.4 | 3.4 | +747.7% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 52.02
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 29.49
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
| Consumption (kWh/mo) | 5200.0 | 6856.3 | +31.9% | ❌ |
| System Cost (USD) | $5,573 | $7,200 | +29.2% | ⚠️ |
| System Cost (R) | R103,100 | R133,200 | +29.2% | ⚠️ |
| Monthly Savings (USD) | $956.76 | $378.76 | -60.4% | ❌ |
| Monthly Savings (R) | R17,700 | R7,007 | -60.4% | ❌ |
| Payback (years) | 0.5 | 1.6 | +216.8% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 57.35
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 63.13
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
| Consumption (kWh/mo) | 3600.0 | 7343.9 | +104.0% | ❌ |
| System Cost (USD) | $3,543 | $8,640 | +143.9% | ❌ |
| System Cost (KES) | KES496,000 | KES1,209,600 | +143.9% | ❌ |
| Monthly Savings (USD) | $557.14 | $192.56 | -65.4% | ❌ |
| Monthly Savings (KES) | KES78,000 | KES26,958 | -65.4% | ❌ |
| Payback (years) | 0.5 | 3.7 | +647.8% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 48.86
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 26.74
- **Energy Scenario:** grid_only

---
