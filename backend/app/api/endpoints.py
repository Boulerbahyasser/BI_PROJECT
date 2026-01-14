from fastapi import APIRouter, Query
from ..data_provider import data_provider
from ..analytics import get_kpi_overview, get_top_products, get_sales_timeseries
from ..ml_models import perform_segmentation, forecast_sales

router = APIRouter()

@router.get("/kpis/overview")
def kpis(country: str = None):
    return get_kpi_overview(country=country)

@router.get("/sales/top-products")
def top_products(limit: int = 10):
    return get_top_products(limit=limit)

@router.get("/sales/timeseries")
def timeseries(granularity: str = 'month'):
    return get_sales_timeseries(granularity=granularity)

@router.get("/ml/segments/summary")
def ml_segments(clusters: int = 4):
    return perform_segmentation(n_clusters=clusters)

@router.get("/ml/predict/forecast")
def ml_forecast(horizon: int = 6):
    return forecast_sales(horizon_months=horizon)

@router.post("/ml/train/xgboost-forecast")
def train_xgboost():
    return train_xgboost_forecast()

@router.post("/ml/predict/xgboost-forecast")
def predict_xgboost(horizon: int = 6):
    return predict_xgboost_forecast(horizon_months=horizon)
