# MODEL 4 TEST SUITE - DETAILED COMPARISON

**Test Date:** 2026-02-26T12:46:55.480412


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
| Consumption (kWh/mo) | 3200.0 | 5556.6 | +73.6% | ❌ |
| System Cost (USD) | $2,555 | $4,600 | +80.1% | ❌ |
| System Cost (₦) | ₦3,960,000 | ₦7,130,000 | +80.1% | ❌ |
| Monthly Savings (USD) | $115.20 | $322.78 | +180.2% | ❌ |
| Monthly Savings (₦) | ₦178,560 | ₦500,309 | +180.2% | ❌ |
| Payback (years) | 1.8 | 1.2 | -34.0% | ⚠️ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 65.94
- **Recommendation:** High
- **Status:** HIGHLY VIABLE
- **ROI %:** 84.2
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
| Consumption (kWh/mo) | 2200.0 | 5847.2 | +165.8% | ❌ |
| System Cost (USD) | $2,088 | $4,400 | +110.7% | ❌ |
| System Cost (GHS) | GHS26,100 | GHS55,000 | +110.7% | ❌ |
| Monthly Savings (USD) | $71.50 | $394.04 | +451.1% | ❌ |
| Monthly Savings (GHS) | GHS894 | GHS4,926 | +451.1% | ❌ |
| Payback (years) | 2.4 | 0.9 | -61.2% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 65.55
- **Recommendation:** High
- **Status:** HIGHLY VIABLE
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
| Consumption (kWh/mo) | 2800.0 | 4735.7 | +69.1% | ❌ |
| System Cost (USD) | $2,500 | $4,320 | +72.8% | ❌ |
| System Cost (KES) | KES350,000 | KES604,800 | +72.8% | ❌ |
| Monthly Savings (USD) | $277.20 | $1210.81 | +336.8% | ❌ |
| Monthly Savings (KES) | KES38,808 | KES169,513 | +336.8% | ❌ |
| Payback (years) | 0.8 | 0.3 | -62.8% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 72.18
- **Recommendation:** High
- **Status:** HIGHLY VIABLE
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
| Consumption (kWh/mo) | 4500.0 | 3474.5 | -22.8% | ❌ |
| System Cost (USD) | $4,832 | $3,349 | -30.7% | ❌ |
| System Cost (R) | R89,400 | R61,963 | -30.7% | ❌ |
| Monthly Savings (USD) | $157.50 | $437.79 | +178.0% | ❌ |
| Monthly Savings (R) | R2,914 | R8,099 | +178.0% | ❌ |
| Payback (years) | 2.6 | 0.6 | -75.5% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 77.0
- **Recommendation:** High
- **Status:** HIGHLY VIABLE
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
| Consumption (kWh/mo) | 3800.0 | 3358.9 | -11.6% | ✅ |
| System Cost (USD) | $2,732 | $3,418 | +25.1% | ⚠️ |
| System Cost (ETB) | ETB153,000 | ETB191,435 | +25.1% | ⚠️ |
| Monthly Savings (USD) | $102.60 | $513.94 | +400.9% | ❌ |
| Monthly Savings (ETB) | ETB5,746 | ETB28,781 | +400.9% | ❌ |
| Payback (years) | 2.2 | 0.6 | -74.8% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 77.0
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
| Consumption (kWh/mo) | 4100.0 | 4649.8 | +13.4% | ✅ |
| System Cost (USD) | $3,716 | $4,320 | +16.2% | ✅ |
| System Cost (UGX) | UGX13,750,000 | UGX15,984,000 | +16.2% | ✅ |
| Monthly Savings (USD) | $205.00 | $374.00 | +82.4% | ❌ |
| Monthly Savings (UGX) | UGX758,500 | UGX1,383,800 | +82.4% | ❌ |
| Payback (years) | 1.5 | 1.0 | -35.8% | ⚠️ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 71.94
- **Recommendation:** High
- **Status:** HIGHLY VIABLE
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
| Consumption (kWh/mo) | 2600.0 | 3221.6 | +23.9% | ❌ |
| System Cost (USD) | $2,265 | $4,025 | +77.7% | ❌ |
| System Cost (RWF) | RWF2,945,000 | RWF5,233,111 | +77.7% | ❌ |
| Monthly Savings (USD) | $280.80 | $990.56 | +252.8% | ❌ |
| Monthly Savings (RWF) | RWF365,040 | RWF1,287,728 | +252.8% | ❌ |
| Payback (years) | 0.7 | 0.3 | -51.6% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 77.0
- **Recommendation:** High
- **Status:** HIGHLY VIABLE
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
| Consumption (kWh/mo) | 2400.0 | 6189.3 | +157.9% | ❌ |
| System Cost (USD) | $1,888 | $4,320 | +128.9% | ❌ |
| System Cost (TZS) | TZS4,436,000 | TZS10,152,000 | +128.9% | ❌ |
| Monthly Savings (USD) | $66.00 | $424.69 | +543.5% | ❌ |
| Monthly Savings (TZS) | TZS155,100 | TZS998,022 | +543.5% | ❌ |
| Payback (years) | 2.4 | 0.8 | -64.7% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 68.71
- **Recommendation:** High
- **Status:** HIGHLY VIABLE
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
| Consumption (kWh/mo) | 5200.0 | 3079.4 | -40.8% | ❌ |
| System Cost (USD) | $5,573 | $2,968 | -46.7% | ❌ |
| System Cost (R) | R103,100 | R54,916 | -46.7% | ❌ |
| Monthly Savings (USD) | $327.60 | $661.80 | +102.0% | ❌ |
| Monthly Savings (R) | R6,061 | R12,243 | +102.0% | ❌ |
| Payback (years) | 1.4 | 0.4 | -73.3% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 77.0
- **Recommendation:** High
- **Status:** HIGHLY VIABLE
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
| Consumption (kWh/mo) | 3600.0 | 6056.1 | +68.2% | ❌ |
| System Cost (USD) | $3,543 | $4,320 | +21.9% | ⚠️ |
| System Cost (KES) | KES496,000 | KES604,800 | +21.9% | ⚠️ |
| Monthly Savings (USD) | $198.00 | $385.12 | +94.5% | ❌ |
| Monthly Savings (KES) | KES27,720 | KES53,917 | +94.5% | ❌ |
| Payback (years) | 1.5 | 0.9 | -37.7% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 67.34
- **Recommendation:** High
- **Status:** HIGHLY VIABLE
- **ROI %:** 100.0
- **Energy Scenario:** grid_only

---
