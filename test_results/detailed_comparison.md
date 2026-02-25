# MODEL 4 TEST SUITE - DETAILED COMPARISON

**Test Date:** 2026-02-25T15:01:11.096770


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
| System Cost (USD) | $2,555 | $34,500 | +1250.4% | ❌ |
| System Cost (₦) | ₦3,960,000 | ₦53,475,000 | +1250.4% | ❌ |
| Monthly Savings (USD) | $464.52 | $158.60 | -65.9% | ❌ |
| Monthly Savings (₦) | ₦720,000 | ₦245,830 | -65.9% | ❌ |
| Payback (years) | 0.5 | 18.1 | +3525.5% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 23.05
- **Recommendation:** Low
- **Status:** NOT VIABLE
- **ROI %:** 5.52
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
| System Cost (USD) | $2,088 | $33,000 | +1480.5% | ❌ |
| System Cost (GHS) | GHS26,100 | GHS412,500 | +1480.5% | ❌ |
| Monthly Savings (USD) | $380.16 | $197.02 | -48.2% | ❌ |
| Monthly Savings (GHS) | GHS4,752 | GHS2,463 | -48.2% | ❌ |
| Payback (years) | 0.5 | 14.0 | +2691.6% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 25.64
- **Recommendation:** Low
- **Status:** NOT VIABLE
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
| Consumption (kWh/mo) | 2800.0 | 4882.3 | +74.4% | ❌ |
| System Cost (USD) | $2,500 | $32,400 | +1196.0% | ❌ |
| System Cost (KES) | KES350,000 | KES4,536,000 | +1196.0% | ❌ |
| Monthly Savings (USD) | $905.36 | $603.74 | -33.3% | ❌ |
| Monthly Savings (KES) | KES126,750 | KES84,524 | -33.3% | ❌ |
| Payback (years) | 0.2 | 4.5 | +2136.1% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 49.73
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 22.36
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
| System Cost (USD) | $4,832 | $27,000 | +458.7% | ❌ |
| System Cost (R) | R89,400 | R499,500 | +458.7% | ❌ |
| Monthly Savings (USD) | $634.86 | $235.28 | -62.9% | ❌ |
| Monthly Savings (R) | R11,745 | R4,353 | -62.9% | ❌ |
| Payback (years) | 0.6 | 9.6 | +1493.8% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 32.36
- **Recommendation:** Low
- **Status:** NOT VIABLE
- **ROI %:** 10.46
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
| System Cost (USD) | $2,732 | $33,600 | +1129.8% | ❌ |
| System Cost (ETB) | ETB153,000 | ETB1,881,600 | +1129.8% | ❌ |
| Monthly Savings (USD) | $491.52 | $330.87 | -32.7% | ❌ |
| Monthly Savings (ETB) | ETB27,525 | ETB18,529 | -32.7% | ❌ |
| Payback (years) | 0.5 | 8.5 | +1592.5% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 40.96
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 11.82
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
| System Cost (USD) | $3,716 | $32,400 | +771.9% | ❌ |
| System Cost (UGX) | UGX13,750,000 | UGX119,880,000 | +771.9% | ❌ |
| Monthly Savings (USD) | $1195.95 | $187.00 | -84.4% | ❌ |
| Monthly Savings (UGX) | UGX4,425,000 | UGX691,900 | -84.4% | ❌ |
| Payback (years) | 0.3 | 14.4 | +4712.8% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 24.07
- **Recommendation:** Low
- **Status:** NOT VIABLE
- **ROI %:** 6.93
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
| System Cost (USD) | $2,265 | $32,400 | +1330.2% | ❌ |
| System Cost (RWF) | RWF2,945,000 | RWF42,120,000 | +1330.2% | ❌ |
| Monthly Savings (USD) | $1125.00 | $518.10 | -53.9% | ❌ |
| Monthly Savings (RWF) | RWF1,462,500 | RWF673,530 | -53.9% | ❌ |
| Payback (years) | 0.2 | 5.2 | +2505.7% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 48.54
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 19.19
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
| System Cost (USD) | $1,888 | $32,400 | +1616.4% | ❌ |
| System Cost (TZS) | TZS4,436,000 | TZS76,140,000 | +1616.4% | ❌ |
| Monthly Savings (USD) | $367.02 | $212.35 | -42.1% | ❌ |
| Monthly Savings (TZS) | TZS862,500 | TZS499,022 | -42.1% | ❌ |
| Payback (years) | 0.4 | 12.7 | +3078.7% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 27.88
- **Recommendation:** Low
- **Status:** NOT VIABLE
- **ROI %:** 7.86
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
| System Cost (USD) | $5,573 | $27,000 | +384.5% | ❌ |
| System Cost (R) | R103,100 | R499,500 | +384.5% | ❌ |
| Monthly Savings (USD) | $956.76 | $378.76 | -60.4% | ❌ |
| Monthly Savings (R) | R17,700 | R7,007 | -60.4% | ❌ |
| Payback (years) | 0.5 | 5.9 | +1088.1% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 40.1
- **Recommendation:** Medium
- **Status:** MODERATELY VIABLE
- **ROI %:** 16.83
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
| System Cost (USD) | $3,543 | $32,400 | +814.5% | ❌ |
| System Cost (KES) | KES496,000 | KES4,536,000 | +814.5% | ❌ |
| Monthly Savings (USD) | $557.14 | $192.56 | -65.4% | ❌ |
| Monthly Savings (KES) | KES78,000 | KES26,958 | -65.4% | ❌ |
| Payback (years) | 0.5 | 14.0 | +2704.3% | ❌ |

### 🔍 API Response (Key Fields)

- **Viability Score:** 25.35
- **Recommendation:** Low
- **Status:** NOT VIABLE
- **ROI %:** 7.13
- **Energy Scenario:** grid_only

---
