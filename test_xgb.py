from backend.app.ml_models import train_xgboost_forecast, predict_xgboost_forecast
from backend.app.data_provider import data_provider
import logging
import traceback

logging.basicConfig(level=logging.INFO)

def test_xgb():
    try:
        print("Explicitly loading data...")
        df = data_provider.load_data()
        if df is None:
            print(f"Data load failed: {data_provider.status}")
            return
            
        print(f"Data loaded: {len(df)} rows.")
        
        print("\nTesting train_xgboost_forecast()...")
        result = train_xgboost_forecast()
        print(f"Train Result: {result}")
        
        if "error" not in result:
            print("\nTesting predict_xgboost_forecast()...")
            preds = predict_xgboost_forecast(horizon_months=3)
            print(f"Predictions: {preds}")
            
    except Exception as e:
        print("XGBoost Test Crashed:")
        traceback.print_exc()

if __name__ == "__main__":
    test_xgb()
