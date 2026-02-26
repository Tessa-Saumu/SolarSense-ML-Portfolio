# MODEL 4 TEST SUITE - EXECUTIVE SUMMARY

**Test Date:** 2026-02-26T12:46:55.480412

**API Endpoint:** https://dse-models-production.up.railway.app/api/v1/analyze

## 📊 Overall Results

- **Total Tests:** 10
- **✅ Passed:** 0
- **⚠️  Warnings:** 0
- **❌ Failed:** 10
- **🔥 Errors:** 0

**Pass Rate:** 0.0%

## 📋 Test Results Summary

| Profile | Country | Status | Issues |
|---------|---------|--------|--------|
| Lagos Fresh Cuts Butchery | Nigeria | ❌ FAIL | consumption_kwh, system_cost, monthly_savings |
| Accra Daily Grocery | Ghana | ❌ FAIL | consumption_kwh, system_cost, monthly_savings, payback_years |
| Nairobi Bread Haven Bakery | Kenya | ❌ FAIL | consumption_kwh, system_cost, monthly_savings, payback_years |
| Johannesburg ChillMart Superma | South Africa | ❌ FAIL | consumption_kwh, system_cost, monthly_savings, payback_years |
| Addis Ice Foods Frozen Retail | Ethiopia | ❌ FAIL | monthly_savings, payback_years |
| Kampala Farm Cold Storage | Uganda | ❌ FAIL | monthly_savings |
| Kigali Quick Freeze Butchery | Rwanda | ❌ FAIL | consumption_kwh, system_cost, monthly_savings, payback_years |
| Dar Fresh Mart Grocery | Tanzania | ❌ FAIL | consumption_kwh, system_cost, monthly_savings, payback_years |
| Cape Meat Locker Cold Storage | South Africa | ❌ FAIL | consumption_kwh, system_cost, monthly_savings, payback_years |
| Nairobi Frosty Mini Mart | Kenya | ❌ FAIL | consumption_kwh, monthly_savings, payback_years |

## 🎯 Tolerance Thresholds

- **Consumption:** ±15%
- **System Cost:** ±20%
- **Monthly Savings:** ±20%
- **Payback Period:** ±25%

## 🔍 Key Findings

### Issues Identified:

- **monthly_savings**: 10 profiles affected
- **payback_years**: 10 profiles affected
- **system_cost**: 9 profiles affected
- **consumption_kwh**: 8 profiles affected

---

*For detailed profile-by-profile comparison, see `detailed_comparison.md`*
