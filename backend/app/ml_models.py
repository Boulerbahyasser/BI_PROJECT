import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import numpy as np
from .data_provider import data_provider

def perform_segmentation(n_clusters=4):
    df = data_provider.get_data()
    if df is None: return {"summary": {}, "segments": []}
    
    df_clean = df[~df['is_return']]
    
    # RFM
    snapshot_date = df_clean['InvoiceDate'].max() + pd.Timedelta(days=1)
    rfm = df_clean.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
        'InvoiceNo': 'nunique',
        'TotalPrice': 'sum'
    })
    rfm.columns = ['Recency', 'Frequency', 'Monetary']
    
    # Scaling
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm)
    
    # KMeans
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    rfm['Segment'] = kmeans.fit_predict(rfm_scaled)
    
    summary = rfm.groupby('Segment').agg({
        'Recency': 'mean',
        'Frequency': 'mean',
        'Monetary': ['mean', 'count']
    }).round(2)
    
    # Flatten multi-index columns for JSON serialization
    # From ('Monetary', 'mean') to 'Monetary_mean'
    summary.columns = [f"{col[0]}_{col[1]}" if isinstance(col, tuple) else col for col in summary.columns]
    
    return {
        "summary": summary.to_dict(),
        "segments": rfm.reset_index().rename(columns={'CustomerID': 'CustomerID'}).to_dict(orient='records')[:100]
    }

import xgboost as xgb
from sklearn.metrics import mean_absolute_error
import joblib

# Global model storage for XGBoost
xgb_model_instance = None
xgb_metadata = {}

def prepare_forecast_features(df_clean):
    """Aggregate CA by month and create temporal features."""
    monthly_sales = df_clean.groupby('MonthStr')['TotalPrice'].sum().reset_index()
    monthly_sales.columns = ['Month', 'TotalPrice']
    monthly_sales['MonthDate'] = pd.to_datetime(monthly_sales['Month'])
    monthly_sales = monthly_sales.sort_values('MonthDate')
    
    # Feature Engineering
    monthly_sales['year'] = monthly_sales['MonthDate'].dt.year
    monthly_sales['month'] = monthly_sales['MonthDate'].dt.month
    monthly_sales['quarter'] = monthly_sales['MonthDate'].dt.quarter
    monthly_sales['month_index'] = np.arange(len(monthly_sales))
    
    return monthly_sales

def train_xgboost_forecast():
    """Train XGBoost model on historical data."""
    global xgb_model_instance, xgb_metadata
    
    df = data_provider.get_data()
    if df is None: return {"error": "No data available"}
    
    df_clean = df[~df['is_return']]
    data = prepare_forecast_features(df_clean)
    
    if len(data) < 4:
        return {"error": "Not enough historical data for XGBoost (min 4 months)"}
    
    # Temporal Split (last 2 months for testing)
    train_size = int(len(data) * 0.8)
    train, test = data.iloc[:train_size], data.iloc[train_size:]
    
    features = ['year', 'month', 'quarter', 'month_index']
    X_train, y_train = train[features], train['TotalPrice']
    X_test, y_test = test[features], test['TotalPrice']
    
    # Stable XGBoost Parameters
    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        objective='reg:squarederror',
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Evaluation
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    
    # Feature Importance
    importance = dict(zip(features, [float(x) for x in model.feature_importances_]))
    
    xgb_model_instance = model
    xgb_metadata = {
        "mae": round(float(mae), 2),
        "last_index": data['month_index'].max(),
        "last_date": data['MonthDate'].max(),
        "importance": importance
    }
    
    return {
        "status": "success",
        "mae": xgb_metadata["mae"],
        "importance": importance
    }

def predict_xgboost_forecast(horizon_months=6):
    """Predict future sales using trained XGBoost model."""
    global xgb_model_instance, xgb_metadata
    
    if xgb_model_instance is None:
        # Auto-train if not trained
        train_xgboost_forecast()
        if xgb_model_instance is None:
            return []
            
    last_date = xgb_metadata["last_date"]
    last_index = xgb_metadata["last_index"]
    
    future_dates = pd.date_range(start=last_date, periods=horizon_months + 1, freq='M')[1:]
    
    future_data = []
    for i, date in enumerate(future_dates):
        current_idx = last_index + i + 1
        future_data.append({
            "year": date.year,
            "month": date.month,
            "quarter": date.quarter,
            "month_index": current_idx,
            "date": date.strftime('%Y-%m')
        })
    
    future_df = pd.DataFrame(future_data)
    features = ['year', 'month', 'quarter', 'month_index']
    
    preds = xgb_model_instance.predict(future_df[features])
    
    result = []
    for i, pred in enumerate(preds):
        result.append({
            "date": future_df.iloc[i]['date'],
            "prediction": round(float(pred), 2)
        })
        
    return result

def forecast_sales(horizon_months=6):
    """Old Linear Regression model for comparison."""
    df = data_provider.get_data()
    if df is None: return []
    
    df_clean = df[~df['is_return']]
    monthly_sales = prepare_forecast_features(df_clean)
    
    X = monthly_sales[['month_index']]
    y = monthly_sales['TotalPrice']
    
    model = LinearRegression()
    model.fit(X, y)
    
    future_X = np.arange(len(monthly_sales), len(monthly_sales) + horizon_months).reshape(-1, 1)
    forecast = model.predict(future_X)
    
    future_dates = pd.date_range(start=monthly_sales['MonthDate'].max(), periods=horizon_months + 1, freq='M')[1:]
    
    result = []
    for date, pred in zip(future_dates, forecast):
        result.append({"date": date.strftime('%Y-%m'), "prediction": round(float(pred), 2)})
        
    return result

def get_loyalty_stats():
    df = data_provider.get_data()
    if df is None: return {"segments": []}
    
    df_clean = df[~df['is_return']]
    
    snapshot_date = df_clean['InvoiceDate'].max() + pd.Timedelta(days=1)
    rfm = df_clean.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
        'InvoiceNo': 'nunique',
        'TotalPrice': 'sum'
    })
    rfm.columns = ['Recency', 'Frequency', 'Monetary']
    
    # Simple Scoring (1-3)
    rfm['R_Score'] = pd.qcut(rfm['Recency'], 3, labels=[3, 2, 1])
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 3, labels=[1, 2, 3])
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], 3, labels=[1, 2, 3])
    
    rfm['RFM_Score'] = rfm[['R_Score', 'F_Score', 'M_Score']].sum(axis=1)
    
    def label_segment(score):
        if score >= 8: return 'Client Fidèle'
        if score >= 5: return 'Client Important'
        return 'Client Perdu'
    
    rfm['Segment'] = rfm['RFM_Score'].apply(label_segment)
    
    segments = rfm['Segment'].value_counts(normalize=True).round(4) * 100
    counts = rfm['Segment'].value_counts()
    
    result = []
    for name, percentage in segments.items():
        result.append({
            "name": name,
            "percentage": percentage,
            "count": int(counts[name])
        })
        
    return {
        "segments": result,
        "total_clients": int(len(rfm))
    }
