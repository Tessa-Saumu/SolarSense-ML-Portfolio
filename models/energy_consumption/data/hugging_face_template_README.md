# Energy Consumption Prediction Model

A Random Forest model for predicting household energy consumption patterns and costs.

## Model Description

This model predicts monthly energy consumption in kWh and associated costs in PLN (Polish Złoty) based on historical consumption patterns and seasonal features.

**Model Type:** Random Forest Regressor  
**Framework:** scikit-learn  
**Performance:** R² = 0.848  

## Features

The model uses 17 engineered features including:
- **Moving averages** (3-month and 6-month windows)
- **Lag features** (1, 2, 3 months back)
- **Seasonal indicators** (winter, summer, transition periods)
- **Temporal features** (month, year, day of year, quarter)
- **Cyclical encoding** (sin/cos transforms for monthly patterns)

## Usage

```python
import sys
sys.path.append('.')  # Add current directory to path

from model import EnergyConsumptionPredictor

# Load the pre-trained model
model = EnergyConsumptionPredictor.from_file('energy_model_latest.joblib')

# Make predictions for next 6 months
predictions = model.predict_future(months=6)

# Display results
print(predictions[['Date', 'Predicted_Consumption', 'Predicted_Cost']])
```

## Output Format

The model returns a pandas DataFrame with columns:
- `Date`: Month start date
- `Predicted_Consumption`: Predicted consumption in kWh
- `Predicted_Cost`: Predicted cost in PLN
- `Month`: Month number (1-12)
- `Year`: Year

## Requirements

```
pandas>=2.0.0
scikit-learn>=1.3.0
numpy>=1.24.0
joblib>=1.3.0
```

## Model Training Data

The model was trained on residential energy consumption data with:
- **17 data points** spanning multiple months
- Features include seasonal patterns, consumption history, and temporal indicators
- Target variable: Monthly energy consumption in kWh

## Performance Metrics

- **R² Score:** 0.848
- **Model Type:** Random Forest (100 estimators)
- **Cross-validation:** 3-fold CV used for model selection

## Feature Importance

Top 5 most important features:
1. `consumption_ma_3` (3-month moving average)
2. `consumption_ma_6` (6-month moving average) 
3. `consumption_lag_1` (1-month lag)
4. `consumption_lag_3` (3-month lag)
5. `month_sin` (seasonal encoding)

## Cost Calculation

The model calculates costs using Polish energy pricing structure:
- Energy rate per kWh
- Distribution fees
- VAT (Value Added Tax)

## Limitations

- Model is trained on Polish residential data
- Cost calculations use Polish energy pricing
- Designed for monthly predictions
- Performance may vary for different consumption patterns

## Example Output

```
        Date  Predicted_Consumption  Predicted_Cost
0 2025-06-01                    191              216
1 2025-07-01                    135              153
2 2025-08-01                    199              224
```

## License

This model is provided as-is for demonstration and educational purposes.
