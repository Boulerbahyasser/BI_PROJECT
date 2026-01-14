from backend.app.data_provider import data_provider
from backend.app.analytics import get_kpi_overview
import logging

logging.basicConfig(level=logging.INFO)

def test():
    print("Loading data...")
    df = data_provider.load_data()
    if df is None:
        print(f"Failed to load data. Status: {data_provider.status}")
        return
    
    print(f"Data loaded. Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    try:
        print("Running KPI overview...")
        kpis = get_kpi_overview()
        print(f"KPIs: {kpis}")
    except Exception as e:
        import traceback
        print("Crash in get_kpi_overview:")
        traceback.print_exc()

if __name__ == "__main__":
    test()
