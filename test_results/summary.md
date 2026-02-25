# MODEL 4 TEST SUITE - EXECUTIVE SUMMARY

**Test Date:** 2026-02-25T13:00:30.844444

**API Endpoint:** https://dse-models-production.up.railway.app/api/v1/analyze

## 📊 Overall Results

- **Total Tests:** 10
- **✅ Passed:** 0
- **⚠️  Warnings:** 0
- **❌ Failed:** 5
- **🔥 Errors:** 5

**Pass Rate:** 0.0%

## 📋 Test Results Summary

| Profile | Country | Status | Issues |
|---------|---------|--------|--------|
| Lagos Fresh Cuts Butchery | Nigeria | ❌ FAIL | consumption_kwh, system_cost, monthly_savings, payback_years |
| Accra Daily Grocery | N/A | 🔥 FAILED | API Error: Bad Request |
| Nairobi Bread Haven Bakery | Kenya | ❌ FAIL | consumption_kwh, system_cost, monthly_savings, payback_years |
| Johannesburg ChillMart Superma | N/A | 🔥 FAILED | API Error: Bad Request |
| Addis Ice Foods Frozen Retail | Ethiopia | ❌ FAIL | consumption_kwh, system_cost, monthly_savings, payback_years |
| Kampala Farm Cold Storage | N/A | 🔥 FAILED | API Error: Bad Request |
| Kigali Quick Freeze Butchery | Rwanda | ❌ FAIL | consumption_kwh, system_cost, monthly_savings, payback_years |
| Dar Fresh Mart Grocery | N/A | 🔥 FAILED | API Error: Bad Request |
| Cape Meat Locker Cold Storage | South Africa | ❌ FAIL | consumption_kwh, system_cost, monthly_savings, payback_years |
| Nairobi Frosty Mini Mart | N/A | 🔥 FAILED | API Error: Bad Request |

## 🎯 Tolerance Thresholds

- **Consumption:** ±15%
- **System Cost:** ±20%
- **Monthly Savings:** ±20%
- **Payback Period:** ±25%

## 🔍 Key Findings

### Issues Identified:

- **consumption_kwh**: 5 profiles affected
- **system_cost**: 5 profiles affected
- **monthly_savings**: 5 profiles affected
- **payback_years**: 5 profiles affected

---

*For detailed profile-by-profile comparison, see `detailed_comparison.md`*
