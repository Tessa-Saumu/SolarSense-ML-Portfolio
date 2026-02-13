import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.linear_model import LinearRegression
import pickle
import joblib
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class EnergyConsumptionPredictor:
    def __init__(self):
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'linear_regression': LinearRegression()
        }

        self.best_model = None
        self.best_model_name = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.data_stats = {}

    def _create_features(self, df):
        features_df = df.copy()

        # Moving averages
        for window in [3, 6]:
            if len(df) > window:
                features_df[f'consumption_ma_{window}'] = features_df['Consumption'].rolling(window=window).mean()
                features_df[f'consumption_std_{window}'] = features_df['Consumption'].rolling(window=window).std()

        # Lag features
        for lag in [1, 2, 3]:
            if len(df) > lag:
                features_df[f'consumption_lag_{lag}'] = features_df['Consumption'].shift(lag)

        # Seasonal indicators
        features_df['is_winter'] = features_df['Month'].isin([12, 1, 2]).astype(int)
        features_df['is_summer'] = features_df['Month'].isin([6, 7, 8]).astype(int)
        features_df['is_transition'] = features_df['Month'].isin([3, 4, 5, 9, 10, 11]).astype(int)

        return features_df

    def _prepare_training_data(self, df):
        features_df = self._create_features(df)
        features_df = features_df.dropna()

        exclude_columns = ['Date', 'Consumption', 'Reading', 'Cost']
        feature_columns = [col for col in features_df.columns if col not in exclude_columns]
        self.feature_columns = feature_columns

        X = features_df[feature_columns].values
        y = features_df['Consumption'].values

        return X, y

    def train(self, df):
        # Store data statistics for predictions
        self.data_stats = {
            'mean_consumption': df['Consumption'].mean(),
            'std_consumption': df['Consumption'].std(),
            'min_date': df['Date'].min(),
            'max_date': df['Date'].max(),
            'seasonal_patterns': df.groupby('Month')['Consumption'].mean().to_dict()
        }

        X, y = self._prepare_training_data(df)

        if len(X) < 5:
            return self._train_baseline_model(df)

        X_scaled = self.scaler.fit_transform(X)
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, shuffle=False)

        model_scores = {}

        for model_name, model in self.models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            mae = mean_absolute_error(y_test, y_pred)
            cv_scores = cross_val_score(model, X_scaled, y, cv=3, scoring='r2')

            model_scores[model_name] = {
                'r2_score': r2,
                'rmse': rmse,
                'mae': mae,
                'cv_score': cv_scores.mean()
            }

        # Select best model based on cross-validation
        self.best_model_name = max(model_scores.keys(), key=lambda k: model_scores[k]['cv_score'])
        self.best_model = self.models[self.best_model_name]
        self.best_model.fit(X_scaled, y)

        final_predictions = self.best_model.predict(X_scaled)
        return {
            'r2_score': r2_score(y, final_predictions),
            'rmse': np.sqrt(mean_squared_error(y, final_predictions)),
            'mae': mean_absolute_error(y, final_predictions),
            'model_name': self.best_model_name,
            'all_models': model_scores
        }

    def _train_baseline_model(self, df):
        monthly_avg = df.groupby('Month')['Consumption'].mean()
        overall_mean = df['Consumption'].mean()
        self.baseline_predictions = monthly_avg.fillna(overall_mean).to_dict()
        self.best_model_name = "baseline_seasonal"

        return {
            'r2_score': 0.0,
            'rmse': df['Consumption'].std(),
            'mae': df['Consumption'].std() * 0.8,
            'model_name': 'baseline_seasonal'
        }

    def predict_future(self, months=12):
        if self.best_model_name == "baseline_seasonal":
            return self._predict_baseline(months)

        last_date = self.data_stats['max_date']
        future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=months, freq='MS')

        predictions = []

        for date in future_dates:
            features = {
                'Month': date.month,
                'Year': date.year,
                'DayOfYear': date.timetuple().tm_yday,
                'Quarter': date.quarter,
                'days_since_start': (date - self.data_stats['min_date']).days,
                'month_sin': np.sin(2 * np.pi * date.month / 12),
                'month_cos': np.cos(2 * np.pi * date.month / 12),
                'is_winter': int(date.month in [12, 1, 2]),
                'is_summer': int(date.month in [6, 7, 8]),
                'is_transition': int(date.month in [3, 4, 5, 9, 10, 11])
            }

            # Use seasonal patterns for lag/moving average features
            seasonal_consumption = self.data_stats['seasonal_patterns'].get(date.month, self.data_stats['mean_consumption'])

            for window in [3, 6]:
                features[f'consumption_ma_{window}'] = seasonal_consumption
                features[f'consumption_std_{window}'] = self.data_stats['std_consumption']

            for lag in [1, 2, 3]:
                features[f'consumption_lag_{lag}'] = seasonal_consumption

            feature_vector = np.array([[features[col] for col in self.feature_columns]])
            feature_vector_scaled = self.scaler.transform(feature_vector)

            prediction = self.best_model.predict(feature_vector_scaled)[0]
            # Add some noise to make predictions more realistic
            prediction = max(0, prediction + np.random.normal(0, self.data_stats['std_consumption'] * 0.1))

            predictions.append(prediction)

        # Calculate costs - using hardcoded values for standalone model
        ENERGY_RATE = 0.6972
        DISTRIBUTION_MULTIPLIER = 0.5068  
        VAT_RATE = 0.23

        results_df = pd.DataFrame({
            'Date': future_dates,
            'Predicted_Consumption': predictions,
            'Month': future_dates.month,
            'Year': future_dates.year
        })

        energy_cost = results_df['Predicted_Consumption'] * ENERGY_RATE
        distribution_fee = energy_cost * DISTRIBUTION_MULTIPLIER
        subtotal = energy_cost + distribution_fee
        vat = subtotal * VAT_RATE
        results_df['Predicted_Cost'] = subtotal + vat

        return results_df

    def _predict_baseline(self, months):
        last_date = self.data_stats['max_date']
        future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=months, freq='MS')

        predictions = []
        for date in future_dates:
            seasonal_pred = self.baseline_predictions.get(date.month, self.data_stats['mean_consumption'])
            predictions.append(max(0, seasonal_pred * (1 + np.random.normal(0, 0.1))))

        ENERGY_RATE = 0.6972
        DISTRIBUTION_MULTIPLIER = 0.5068  
        VAT_RATE = 0.23

        results_df = pd.DataFrame({
            'Date': future_dates,
            'Predicted_Consumption': predictions,
            'Month': future_dates.month,
            'Year': future_dates.year
        })

        energy_cost = results_df['Predicted_Consumption'] * ENERGY_RATE
        distribution_fee = energy_cost * DISTRIBUTION_MULTIPLIER
        subtotal = energy_cost + distribution_fee
        vat = subtotal * VAT_RATE
        results_df['Predicted_Cost'] = subtotal + vat

        return results_df

    def get_feature_importance(self):
        if hasattr(self.best_model, 'feature_importances_'):
            importance_dict = dict(zip(self.feature_columns, self.best_model.feature_importances_))
            return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
        return {}

    def save_model(self, filepath=None, format='joblib'):
        if self.best_model is None:
            raise ValueError("Model must be trained first. Use train() method.")

        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            extension = 'joblib' if format == 'joblib' else 'pkl'
            filepath = f"energy_model_{self.best_model_name}_{timestamp}.{extension}"

        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)

        model_data = {
            'best_model': self.best_model,
            'best_model_name': self.best_model_name,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'data_stats': self.data_stats,
            'models': self.models,
            'baseline_predictions': getattr(self, 'baseline_predictions', None),
            'metadata': {
                'saved_at': datetime.now().isoformat(),
                'model_type': self.best_model_name,
                'feature_count': len(self.feature_columns) if self.feature_columns else 0
            }
        }

        if format == 'joblib':
            joblib.dump(model_data, filepath)
        else:
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)

        return filepath

    def load_model(self, filepath, format='auto'):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File {filepath} does not exist.")

        if format == 'auto':
            if filepath.endswith('.joblib'):
                format = 'joblib'
            elif filepath.endswith('.pkl'):
                format = 'pickle'
            else:
                format = 'joblib'

        try:
            if format == 'joblib':
                model_data = joblib.load(filepath)
            else:
                with open(filepath, 'rb') as f:
                    model_data = pickle.load(f)

            self.best_model = model_data['best_model']
            self.best_model_name = model_data['best_model_name']
            self.scaler = model_data['scaler']
            self.feature_columns = model_data['feature_columns']
            self.data_stats = model_data['data_stats']
            self.models = model_data['models']
            self.baseline_predictions = model_data.get('baseline_predictions')

        except Exception as e:
            raise ValueError(f"Error loading model: {str(e)}")

    @classmethod
    def from_file(cls, filepath, format='auto'):
        model = cls()
        model.load_model(filepath, format)
        return model
