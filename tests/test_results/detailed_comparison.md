# MODEL 4 TEST SUITE - DETAILED COMPARISON

**Test Date:** 2026-02-25T15:51:21.614119


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
| Consumption (kWh/mo) | 3200.0 | 5916.6 | +84.9% | ❌ |
| System Cost (USD) | $2,555 | $2,300 | -10.0% | ✅ |
| System Cost (₦) | ₦3,960,000 | ₦3,565,000 | -10.0% | ✅ |
| Monthly Savings (USD) | $115.20 | $159.45 | +38.4% | ❌ |
| Monthly Savings (₦) | ₦178,560 | ₦247,147 | +38.4% | ❌ |
| Payback (years) | 1.8 | 1.2 | -33.2% | ⚠️ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 57.48
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 83.19
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
| System Cost (USD) | $2,088 | $2,200 | +5.4% | ✅ |
| System Cost (GHS) | GHS26,100 | GHS27,500 | +5.4% | ✅ |
| Monthly Savings (USD) | $71.50 | $197.02 | +175.6% | ❌ |
| Monthly Savings (GHS) | GHS894 | GHS2,463 | +175.6% | ❌ |
| Payback (years) | 2.4 | 0.9 | -61.2% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 57.4
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 100.0
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
| Consumption (kWh/mo) | 2800.0 | 4915.7 | +75.6% | ❌ |
| System Cost (USD) | $2,500 | $2,160 | -13.6% | ✅ |
| System Cost (KES) | KES350,000 | KES302,400 | -13.6% | ✅ |
| Monthly Savings (USD) | $277.20 | $603.37 | +117.7% | ❌ |
| Monthly Savings (KES) | KES38,808 | KES84,472 | +117.7% | ❌ |
| Payback (years) | 0.8 | 0.3 | -62.7% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 60.68
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 100.0
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
| Consumption (kWh/mo) | 4500.0 | 4014.5 | -10.8% | ✅ |
| System Cost (USD) | $4,832 | $1,800 | -62.8% | ❌ |
| System Cost (R) | R89,400 | R33,300 | -62.8% | ❌ |
| Monthly Savings (USD) | $157.50 | $235.28 | +49.4% | ❌ |
| Monthly Savings (R) | R2,914 | R4,353 | +49.4% | ❌ |
| Payback (years) | 2.6 | 0.6 | -75.5% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 62.56
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 100.0
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
| System Cost (USD) | $2,732 | $2,240 | -18.0% | ✅ |
| System Cost (ETB) | ETB153,000 | ETB125,440 | -18.0% | ✅ |
| Monthly Savings (USD) | $102.60 | $330.87 | +222.5% | ❌ |
| Monthly Savings (ETB) | ETB5,746 | ETB18,529 | +222.5% | ❌ |
| Payback (years) | 2.2 | 0.6 | -74.4% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 65.73
- **Recommendation:** High
- **Status:** HIGHLY VIABLE
- **ROI %:** 100.0
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
| Consumption (kWh/mo) | 4100.0 | 4889.8 | +19.3% | ⚠️ |
| System Cost (USD) | $3,716 | $2,160 | -41.9% | ❌ |
| System Cost (UGX) | UGX13,750,000 | UGX7,992,000 | -41.9% | ❌ |
| Monthly Savings (USD) | $205.00 | $187.00 | -8.8% | ✅ |
| Monthly Savings (UGX) | UGX758,500 | UGX691,900 | -8.8% | ✅ |
| Payback (years) | 1.5 | 1.0 | -35.8% | ⚠️ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 60.43
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 100.0
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
| Consumption (kWh/mo) | 2600.0 | 3581.6 | +37.8% | ❌ |
| System Cost (USD) | $2,265 | $2,160 | -4.7% | ✅ |
| System Cost (RWF) | RWF2,945,000 | RWF2,808,000 | -4.7% | ✅ |
| Monthly Savings (USD) | $280.80 | $522.78 | +86.2% | ❌ |
| Monthly Savings (RWF) | RWF365,040 | RWF679,614 | +86.2% | ❌ |
| Payback (years) | 0.7 | 0.3 | -50.8% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 63.03
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 100.0
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
| Consumption (kWh/mo) | 2400.0 | 6549.3 | +172.9% | ❌ |
| System Cost (USD) | $1,888 | $2,160 | +14.4% | ✅ |
| System Cost (TZS) | TZS4,436,000 | TZS5,076,000 | +14.4% | ✅ |
| Monthly Savings (USD) | $66.00 | $212.35 | +221.7% | ❌ |
| Monthly Savings (TZS) | TZS155,100 | TZS499,022 | +221.7% | ❌ |
| Payback (years) | 2.4 | 0.8 | -64.7% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 58.84
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 100.0
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
| Consumption (kWh/mo) | 5200.0 | 3439.4 | -33.9% | ❌ |
| System Cost (USD) | $5,573 | $1,800 | -67.7% | ❌ |
| System Cost (R) | R103,100 | R33,300 | -67.7% | ❌ |
| Monthly Savings (USD) | $327.60 | $397.02 | +21.2% | ⚠️ |
| Monthly Savings (R) | R6,061 | R7,345 | +21.2% | ⚠️ |
| Payback (years) | 1.4 | 0.4 | -73.0% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 64.66
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 100.0
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
| Consumption (kWh/mo) | 3600.0 | 6476.1 | +79.9% | ❌ |
| System Cost (USD) | $3,543 | $2,160 | -39.0% | ❌ |
| System Cost (KES) | KES496,000 | KES302,400 | -39.0% | ❌ |
| Monthly Savings (USD) | $198.00 | $192.56 | -2.7% | ✅ |
| Monthly Savings (KES) | KES27,720 | KES26,958 | -2.7% | ✅ |
| Payback (years) | 1.5 | 0.9 | -37.7% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 58.11
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 100.0
- **Energy Scenario:** grid_only

---
