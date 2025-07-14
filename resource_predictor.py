import pandas as pd
import numpy as np
from prophet import Prophet
import streamlit as st

class ResourcePredictor:
    def __init__(self):
        self.models = {}

    def predict_resources(self, resource_type, history_days=30):
        """Predict resource needs for next 7 days for a resource type (beds, doctors, nurses, medications)"""
        try:
            df = self._load_historical_data(resource_type, history_days)
            if len(df) < 7:
                return None

            if resource_type not in self.models:
                self.models[resource_type] = self._train_model(df)
            future = self.models[resource_type].make_future_dataframe(periods=7)
            forecast = self.models[resource_type].predict(future)
            return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(7)
        except Exception as e:
            st.error(f"Prediction failed: {str(e)}")
            return None

    def _load_historical_data(self, resource_type, history_days):
        """Load and prepare historical data. Simulated random data for example."""
        dates = pd.date_range(end=pd.Timestamp.today(), periods=history_days)
        np.random.seed(hash(resource_type) % 123456) # for repeatable results
        values = np.random.randint(20, 50, size=history_days) + np.sin(np.arange(history_days)*0.5)*5
        return pd.DataFrame({'ds': dates, 'y': values})

    def _train_model(self, df):
        """Train Prophet model"""
        model = Prophet(daily_seasonality=True)
        model.fit(df)
        return model

# Singleton instance for easy importing
predictor = ResourcePredictor()

def predict_resources(resource_type):
    """Get predictions with error handling"""
    return predictor.predict_resources(resource_type)