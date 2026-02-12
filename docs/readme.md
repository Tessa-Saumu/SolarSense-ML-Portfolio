# Model 2: Solar Generation Prediction
## NASA POWER API Data Pipeline for SSA Refrigeration SMEs

This module fetches and stores solar irradiance data to assess solar viability for refrigeration-heavy food retail SMEs (butcheries, grocers, mini-supermarkets, cold chain points) in Sub-Saharan Africa.

---

##  Project Overview

**Goal**: Build a solar generation prediction model using NASA POWER API data to determine solar viability for SMEs with high refrigeration energy needs.

**Timeline**: 2-3 weeks (Week 1: Data pipeline, Week 2-3: Model development)

** Tasks**:
- ✅ Set up NASA POWER API data ingestion
- ✅ Create SQL database schema
- ✅ Build data fetching pipeline
- ✅ Query and validate historical solar data
- ✅ Support Tessa with preprocessed data

---

##  Project Structure

```
solar-generation-model/
│
├── notebooks/
│   └── nasa_solar_exploration.ipynb    # Exploration & testing
│
├── src/
│   └── nasa_power_solar_pipeline.py    # Main production pipeline
│
├── sql/
│   └── schema.sql                       # PostgreSQL database schema
│
├── data/
│   └── solar_data_ssa.csv              # Exported data (gitignored)
│
├── config/
│   └── config.yaml                      # Configuration (create this)
│
├── requirements.txt                     # Python dependencies
├── README.md                           # This file
└── .gitignore                          # Git ignore rules
```

---

## Quick Start Guide

### Step 1: Environment Setup

```bash
# Clone your repo (or create new one)
git clone https://github.com/yourusername/solar-generation-model.git
cd solar-generation-model

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Database Setup (PostgreSQL + pgAdmin)

**IMPORTANT**: Read `PGADMIN_SETUP_GUIDE.md` for detailed setup instructions!

**Quick Setup**:
1. Install PostgreSQL and pgAdmin 4
2. Open pgAdmin and create database `solar_irradiance`
3. Open Query Tool and run the `schema.sql` file
4. Update password in `nasa_power_postgresql_pipeline.py`

```bash
# See PGADMIN_SETUP_GUIDE.md for full instructions
```

### Step 3: Run the Pipeline

```bash
# Install PostgreSQL adapter
pip install psycopg2-binary

# Update password in the script first!
# Edit: nasa_power_postgresql_pipeline.py
# Update the DB_CONFIG password

# Then run the pipeline
python nasa_power_postgresql_pipeline.py
```

---

## What the Pipeline Does

1. **Fetches Data**: Connects to NASA POWER API for 7 SSA locations
2. **Cleans Data**: Parses JSON, handles missing values, validates ranges
3. **Stores Data**: Saves to SQL database with proper schema
4. **Validates**: Checks data quality and coverage
5. **Exports**: Creates CSV for sharing with team

**Data Points Per Location**:
- Solar irradiance (GHI, clear-sky GHI)
- Temperature
- Wind speed
- Relative humidity
- **Time range**: Last 2 years (730 days)

---

## Database Schema

### Tables:

1. **`locations`** - SSA cities with coordinates
2. **`solar_irradiance_daily`** - Daily solar data
3. **`solar_irradiance_monthly`** - Aggregated monthly stats

### Key Queries:

```sql
-- Get all data for Nairobi
SELECT * FROM solar_irradiance_daily 
WHERE location_id = (SELECT location_id FROM locations WHERE location_name = 'Nairobi_Kenya')
ORDER BY date DESC;

-- Calculate monthly averages
SELECT 
    EXTRACT(MONTH FROM date) as month,
    AVG(ghi_kwh_m2) as avg_ghi
FROM solar_irradiance_daily
GROUP BY month;
```

---

## 🌍 SSA Locations Covered

| City | Country | Latitude | Longitude |
|------|---------|----------|-----------|
| Nairobi | Kenya | -1.2921 | 36.8219 |
| Lagos | Nigeria | 6.5244 | 3.3792 |
| Accra | Ghana | 5.6037 | -0.1870 |
| Kampala | Uganda | 0.3476 | 32.5825 |
| Dar es Salaam | Tanzania | -6.7924 | 39.2083 |
| Kigali | Rwanda | -1.9706 | 30.1044 |
| Johannesburg | South Africa | -26.2041 | 28.0473 |

---

##  Working Environment

### Where to Work:

- **Jupyter Notebook**: For exploration, testing, visualization
  - `nasa_solar_exploration.ipynb`
  
- **Python Scripts (.py)**: For production pipeline
  - `nasa_power_solar_pipeline.py`
  
- **PostgreSQL/SQLite**: For data storage
  - Use DBeaver, pgAdmin, or command line
  
- **GitHub**: For version control
  - Commit frequently!
  - Push to remote daily

### Typical Workflow:

```
1. Test in Jupyter → 2. Convert to .py → 3. Commit to GitHub
```

---





### .gitignore Example:

```gitignore
# Python
__pycache__/
*.pyc
venv/
.env

# Data
data/*.csv
*.db
*.sqlite

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

---

##  Supporting Tessa (Data Preprocessing)

**What Tessa Needs**:
- Clean CSV with solar data
- Data dictionary explaining columns
- Coverage report (missing data, date ranges)

**How to Help**:

```python
# Export cleaned data
df_all.to_csv('data/solar_data_for_tessa.csv', index=False)

# Create data dictionary
data_dict = {
    'date': 'Date of measurement (YYYY-MM-DD)',
    'location': 'City name',
    'ghi_kwh_m2': 'Global Horizontal Irradiance (kWh/m²/day)',
    'temperature_c': 'Temperature at 2m (Celsius)',
    # ... etc
}
```


---

## 📈 Next Steps (Week 2-3)

1. **Feature Engineering**:
   - Calculate solar angles
   - Add seasonal patterns
   - Weather variability metrics

2. **Model Development**:
   - Train regression model (solar generation prediction)
   - Validate on test locations
   - Tune hyperparameters

3. **Integration**:
   - Connect with Model 1 (energy consumption)
   - Share data with Model 3 (cost-benefit)
   - Support Model 4 (recommendation engine)

---

##  Troubleshooting

### API Rate Limits
```python
# Add delay between requests
import time
time.sleep(2)  # Wait 2 seconds between calls
```

### Missing Data
```python
# Check for -999 values (NASA's missing data flag)
df = df.replace(-999, np.nan)
```

### Database Connection
```python
# Test SQLite connection
import sqlite3
conn = sqlite3.connect('solar_irradiance.db')
print(conn.execute("SELECT COUNT(*) FROM locations").fetchone())
```

---

Resources

- **NASA POWER API Docs**: https://power.larc.nasa.gov/docs/
- **Pandas Docs**: https://pandas.pydata.org/docs/
- **PostgreSQL Tutorial**: https://www.postgresqltutorial.com/
- **Solar Energy Basics**: https://www.nrel.gov/solar/

---

## Team Coordination

**Your Role**: Solar data pipeline + generation prediction  
**Tessa's Role**: Data preprocessing  
**Other Models**: Energy consumption, cost-benefit, recommendations

**Communication**:
- Share cleaned data via CSV
- Document data format clearly
- Flag any data quality issues
- Coordinate on feature engineering

---

Checklist

- [ ] Set up virtual environment
- [ ] Install dependencies
- [ ] Test NASA API connection (Jupyter)
- [ ] Run full pipeline script
- [ ] Create database (SQLite or PostgreSQL)
- [ ] Validate data quality
- [ ] Export data for Tessa
- [ ] Upload code to GitHub
- [ ] Document data format
- [ ] Begin model development

---

**Good luck! You got this!**

