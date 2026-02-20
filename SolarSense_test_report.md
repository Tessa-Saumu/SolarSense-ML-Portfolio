# SolarSense AI – Test Report

## Overview
This report summarizes tests of SolarSense AI across multiple business setups.  
- **Scenario** = User input  
- **Assessment** = System output  
- **Error/Failure** = Cases where the system could not generate an assessment  

---

## Quick Summary Table

| # | Business | Location | Monthly Cost (KSh) | Solar Savings (KSh/mo) | ROI (%) | Viability Score |
|---|---------|---------|------------------|-----------------------|---------|----------------|
| 1 | Restaurant | Nairobi | 30,000 | 30.32 | 5.6 | 44.1 |
| 2 | Butchery | Murang’a | 5,000 | – | – | – (Failed) |
| 3 | Mini Supermarket | Murang’a | 10,000 | – | – | – (Failed) |
| 4 | Hotel | Kiambu | 80,000 | 30.32 | 5.6 | 44.1 |
| 5 | Mini Supermarket | Nairobi | 15,000 | 30.32 | 5.6 | 44.1 |
| 6 | Hotel | Nairobi (Diesel) | 100,000 | 948.79 | 100 | 97.0 |

*Note: “–” indicates assessment failure.*

---

## Scenarios

### 1. Restaurant – Nairobi (On-grid)
- **Monthly Cost:** KSh 30,000  
- **Equipment:** 4x Fridge, 2x Freezer, 10x Mixed Bulbs  

**Assessment:**  
- Energy Use: 225 kWh/mo  
- Solar Generation: 202 kWh/mo  
- Panel Size: 10.8 m²  
- System Cost: KSh 6,474  
- Solar Coverage: 90%  
- Savings: KSh 30.32/mo  
- ROI: 5.6%  
- Viability Score: 44.1/100  

---

### 2. Butchery – Murang’a (On-grid)
- **Monthly Cost:** KSh 5,000  
- **Equipment:** 1x Fridge, 2x Freezer, 2x Fluorescent Bulbs  

**Assessment:** Failed – Invalid input  

---

### 3. Mini Supermarket – Murang’a (Off-grid Diesel)
- **Monthly Cost:** KSh 10,000  
- **Diesel:** 6 hrs/day @ KSh 166.54/liter  
- **Equipment:** 3x Fridge, 2x Freezer, 6x Fluorescent Bulbs  

**Assessment:** Failed – Invalid input  

---

### 4. Hotel – Kiambu (On-grid)
- **Monthly Cost:** KSh 80,000  
- **Equipment:** 10x Fridges, 2x Freezers, 1x Medium Cold Room, 20x LED Bulbs  

**Assessment:**  
- Solar Generation: 202 kWh/mo  
- Panel Size: 10.8 m²  
- System Cost: KSh 6,474  
- Solar Coverage: 90%  
- Savings: KSh 30.32/mo  
- ROI: 5.6%  
- Viability Score: 44.1/100  

---

### 5. Mini Supermarket – Nairobi (On-grid)
- **Monthly Cost:** KSh 15,000  
- **Equipment:** 5x Fridges, 4x Freezers, 6x Mixed Bulbs  

**Assessment:**  
- Solar Generation: 202 kWh/mo  
- Panel Size: 10.8 m²  
- System Cost: KSh 6,474  
- Solar Coverage: 90%  
- Savings: KSh 30.32/mo  
- ROI: 5.6%  
- Viability Score: 44.1/100  

---

### 6. Hotel – Nairobi (Off-grid Diesel)
- **Monthly Cost:** KSh 100,000  
- **Diesel:** 20 hrs/day @ KSh 166.54/liter  
- **Equipment:** 10x Fridges, 5x Freezers, 2x Small Cold Rooms, 18x Mixed Bulbs  

**Assessment:**  
- Solar Generation: 202 kWh/mo  
- Panel Size: 10.8 m²  
- System Cost: KSh 6,474  
- Solar Coverage: 90%  
- Savings: KSh 948.79/mo  
- ROI: 100%  
- Viability Score: 97.0/100  

---

## Summary of Observations & Recommendations

1. **On-grid scenarios:**  
   - Solar coverage looks correct, but savings are **extremely low** relative to actual electricity costs.  
   - Flat energy usage leads to **underestimated ROI** and payback periods.  

2. **Off-grid diesel scenarios:**  
   - Solar offsets diesel costs effectively; ROI reflects this (100% in high consumption).  
   - Some assessments fail due to backend validation issues.  

3. **Failures / Errors:**  
   - Butchery – Murang’a (On-grid)  
   - Mini Supermarket – Murang’a (Off-grid Diesel)  
   - Likely caused by unsupported input combinations or equipment scaling issues.  

4. **Action Items:**  
   - **Update ROI/savings calculations** to use **actual energy per equipment**:  
     - Assign typical kWh/month to each appliance.  
     - Sum total energy for the business.  
     - Calculate savings as solar offset × electricity rate.  
     - Compute ROI: `(Annual savings ÷ System cost) × 100`.  
   - Standardize currency (KSh only).  
   - Include equipment-level energy breakdown.  
   - Fix PDF download.  
   - Improve backend validation and error messaging.