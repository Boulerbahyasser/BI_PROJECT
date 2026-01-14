import pandas as pd
from .data_provider import data_provider

def get_kpi_overview(start_date=None, end_date=None, country=None):
    df = data_provider.get_data()
    if df is None: return {}
    
    # Filtering with proper index alignment
    mask = pd.Series(True, index=df.index)
    if start_date:
        mask &= (df['InvoiceDate'] >= pd.to_datetime(start_date))
    if end_date:
        mask &= (df['InvoiceDate'] <= pd.to_datetime(end_date))
    if country:
        mask &= (df['Country'] == country)
    
    filtered_df = df[mask & (~df['is_return'])]
    
    ca_total = filtered_df['TotalPrice'].sum()
    nb_cmd = filtered_df['InvoiceNo'].nunique()
    panier_moyen = ca_total / nb_cmd if nb_cmd > 0 else 0
    clients_uniques = filtered_df['CustomerID'].nunique()
    
    # Returns
    returns_df = df[mask & df['is_return']]
    taux_retour = (len(returns_df) / len(df[mask])) * 100 if len(df[mask]) > 0 else 0
    
    return {
        "ca_total": round(float(ca_total), 2),
        "nb_commandes": int(nb_cmd),
        "panier_moyen": round(float(panier_moyen), 2),
        "clients_uniques": int(clients_uniques),
        "taux_retour": round(float(taux_retour), 2)
    }

def get_top_products(limit=10):
    df = data_provider.get_data()
    if df is None: return []
    
    top = df[~df['is_return']].groupby(['StockCode', 'Description'])['TotalPrice'].sum().sort_values(ascending=False).head(limit)
    return top.reset_index().to_dict(orient='records')

def get_sales_timeseries(granularity='month'):
    df = data_provider.get_data()
    if df is None: return {}
    
    df_clean = df[~df['is_return']]
    
    if granularity == 'month':
        ts = df_clean.groupby('MonthStr')['TotalPrice'].sum()
        ts.index = ts.index.astype(str)
    else:
        ts = df_clean.groupby(df_clean['InvoiceDate'].dt.date)['TotalPrice'].sum()
        ts.index = ts.index.astype(str)
        
    return ts.to_dict()
