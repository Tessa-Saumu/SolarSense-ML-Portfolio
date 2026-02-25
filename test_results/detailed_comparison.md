# MODEL 4 TEST SUITE - DETAILED COMPARISON

**Test Date:** 2026-02-25T14:23:51.822572


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
| Consumption (kWh/mo) | 3200.0 | 1014.6 | -68.3% | ❌ |
| System Cost (USD) | $2,555 | $23,122 | +805.0% | ❌ |
| System Cost (₦) | ₦3,960,000 | ₦35,839,844 | +805.0% | ❌ |
| Monthly Savings (USD) | $464.52 | $188.12 | -59.5% | ❌ |
| Monthly Savings (₦) | ₦720,000 | ₦291,586 | -59.5% | ❌ |
| Payback (years) | 0.5 | 10.2 | +1948.6% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 49.14
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 9.76
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
| Consumption (kWh/mo) | 2200.0 | 1399.5 | -36.4% | ❌ |
| System Cost (USD) | $2,088 | $27,425 | +1213.5% | ❌ |
| System Cost (GHS) | GHS26,100 | GHS342,818 | +1213.5% | ❌ |
| Monthly Savings (USD) | $380.16 | $163.74 | -56.9% | ❌ |
| Monthly Savings (GHS) | GHS4,752 | GHS2,047 | -56.9% | ❌ |
| Payback (years) | 0.5 | 14.0 | +2691.6% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 45.24
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 7.16
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
| Consumption (kWh/mo) | 2800.0 | 801.9 | -71.4% | ❌ |
| System Cost (USD) | $2,500 | $14,471 | +478.8% | ❌ |
| System Cost (KES) | KES350,000 | KES2,025,925 | +478.8% | ❌ |
| Monthly Savings (USD) | $905.36 | $361.73 | -60.0% | ❌ |
| Monthly Savings (KES) | KES126,750 | KES50,642 | -60.0% | ❌ |
| Payback (years) | 0.2 | 3.3 | +1566.9% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 70.75
- **Recommendation:** High
- **Status:** HIGHLY VIABLE
- **ROI %:** 30.0
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
| Consumption (kWh/mo) | 4500.0 | 644.9 | -85.7% | ❌ |
| System Cost (USD) | $4,832 | $10,526 | +117.8% | ❌ |
| System Cost (R) | R89,400 | R194,734 | +117.8% | ❌ |
| Monthly Savings (USD) | $634.86 | $81.25 | -87.2% | ❌ |
| Monthly Savings (R) | R11,745 | R1,503 | -87.2% | ❌ |
| Payback (years) | 0.6 | 10.8 | +1699.3% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 48.39
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 9.26
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
| Consumption (kWh/mo) | 3800.0 | 308.8 | -91.9% | ❌ |
| System Cost (USD) | $2,732 | $8,400 | +207.5% | ❌ |
| System Cost (ETB) | ETB153,000 | ETB470,400 | +207.5% | ❌ |
| Monthly Savings (USD) | $491.52 | $134.23 | -72.7% | ❌ |
| Monthly Savings (ETB) | ETB27,525 | ETB7,517 | -72.7% | ❌ |
| Payback (years) | 0.5 | 5.2 | +943.0% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 66.27
- **Recommendation:** High
- **Status:** HIGHLY VIABLE
- **ROI %:** 19.18
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
| Consumption (kWh/mo) | 4100.0 | 1070.3 | -73.9% | ❌ |
| System Cost (USD) | $3,716 | $19,889 | +435.2% | ❌ |
| System Cost (UGX) | UGX13,750,000 | UGX73,588,264 | +435.2% | ❌ |
| Monthly Savings (USD) | $1195.95 | $105.96 | -91.1% | ❌ |
| Monthly Savings (UGX) | UGX4,425,000 | UGX392,052 | -91.1% | ❌ |
| Payback (years) | 0.3 | 15.6 | +5113.9% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 44.09
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 6.39
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
| Consumption (kWh/mo) | 2600.0 | 277.9 | -89.3% | ❌ |
| System Cost (USD) | $2,265 | $8,100 | +257.6% | ❌ |
| System Cost (RWF) | RWF2,945,000 | RWF10,530,000 | +257.6% | ❌ |
| Monthly Savings (USD) | $1125.00 | $259.42 | -76.9% | ❌ |
| Monthly Savings (RWF) | RWF1,462,500 | RWF337,246 | -76.9% | ❌ |
| Payback (years) | 0.2 | 2.6 | +1201.0% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 79.02
- **Recommendation:** High
- **Status:** HIGHLY VIABLE
- **ROI %:** 38.43
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
| Consumption (kWh/mo) | 2400.0 | 1451.6 | -39.5% | ❌ |
| System Cost (USD) | $1,888 | $23,754 | +1158.4% | ❌ |
| System Cost (TZS) | TZS4,436,000 | TZS55,821,947 | +1158.4% | ❌ |
| Monthly Savings (USD) | $367.02 | $143.71 | -60.8% | ❌ |
| Monthly Savings (TZS) | TZS862,500 | TZS337,718 | -60.8% | ❌ |
| Payback (years) | 0.4 | 13.8 | +3343.6% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 45.39
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 7.26
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
| Consumption (kWh/mo) | 5200.0 | 824.9 | -84.1% | ❌ |
| System Cost (USD) | $5,573 | $12,921 | +131.9% | ❌ |
| System Cost (R) | R103,100 | R239,047 | +131.9% | ❌ |
| Monthly Savings (USD) | $956.76 | $226.70 | -76.3% | ❌ |
| Monthly Savings (R) | R17,700 | R4,194 | -76.3% | ❌ |
| Payback (years) | 0.5 | 4.7 | +850.0% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 65.16
- **Recommendation:** High
- **Status:** HIGHLY VIABLE
- **ROI %:** 21.05
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
| Consumption (kWh/mo) | 3600.0 | 1628.0 | -54.8% | ❌ |
| System Cost (USD) | $3,543 | $27,120 | +665.5% | ❌ |
| System Cost (KES) | KES496,000 | KES3,796,769 | +665.5% | ❌ |
| Monthly Savings (USD) | $557.14 | $161.18 | -71.1% | ❌ |
| Monthly Savings (KES) | KES78,000 | KES22,565 | -71.1% | ❌ |
| Payback (years) | 0.5 | 14.0 | +2704.3% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 45.19
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 7.13
- **Energy Scenario:** grid_only

---
