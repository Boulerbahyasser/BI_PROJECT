import os
import pandas as pd
from ucimlrepo import fetch_ucirepo
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CACHE_FILE = "online_retail_cache.parquet"

def normalize_column_name(name: str) -> str:
    """Normalize column names: lowercase, strip, remove special characters."""
    if not isinstance(name, str):
        return str(name)
    name = name.lower().strip()
    name = re.sub(r'[^a-z0-9_]', '_', name)
    name = re.sub(r'_+', '_', name)
    return name.strip('_')

def auto_detect_columns(df: pd.DataFrame):
    """Dynamically map standard columns to real columns in the dataframe."""
    logger.info("PHASE 1: Exploring dataset columns...")
    raw_columns = df.columns.tolist()
    logger.info(f"Raw columns detected: {raw_columns}")
    
    normalized_map = {normalize_column_name(col): col for col in raw_columns}
    logger.info(f"Normalized column mapping candidates: {normalized_map}")

    # Define standard column expectations matching the Online Retail dataset exactly
    standard_requirements = {
        "InvoiceNo": ["invoice_no", "invoiceno", "invoice", "no"],
        "StockCode": ["stock_code", "stockcode", "stock", "code"],
        "Description": ["description", "desc"],
        "Quantity": ["quantity", "qty"],
        "InvoiceDate": ["invoice_date", "invoicedate", "date", "time"],
        "UnitPrice": ["unit_price", "unitprice", "price", "rate"],
        "CustomerID": ["customer_id", "customerid", "customer", "id"],
        "Country": ["country", "nation", "region"]
    }

    final_mapping = {}
    missing_cols = []

    for std_name, patterns in standard_requirements.items():
        found = False
        # Try exact normalized match first (std_name.lower())
        std_norm = normalize_column_name(std_name)
        if std_norm in normalized_map:
            final_mapping[std_name] = normalized_map[std_norm]
            found = True
        else:
            # Try patterns
            for pattern in patterns:
                if pattern in normalized_map:
                    final_mapping[std_name] = normalized_map[pattern]
                    found = True
                    break
        
        if not found:
            missing_cols.append(std_name)

    if missing_cols:
        logger.warning(f"CRITICAL: Missing standard columns: {missing_cols}")
        return None, missing_cols

    logger.info(f"Dynamic mapping validated: {final_mapping}")
    return final_mapping, []

import threading

class DataProvider:
    _instance = None
    df = None
    status = "WAITING"
    _lock = threading.Lock()
    _is_loading = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_data(self):
        """3-Phase ETL Pipeline: Explore -> Transform -> Load."""
        with self._lock:
            if self.df is not None or self._is_loading:
                return self.df
            self._is_loading = True

        try:
            self.status = "PHASE 1: EXPLORE"
            df_raw = None

            # Check cache
            if os.path.exists(CACHE_FILE):
                try:
                    logger.info("Loading from local cache...")
                    df_raw = pd.read_parquet(CACHE_FILE)
                except Exception as e:
                    logger.error(f"Cache corrupted: {e}")

            if df_raw is None:
                try:
                    logger.info("Fetching raw data from UCI ML (id=352)...")
                    online_retail = fetch_ucirepo(id=352)
                    df_raw = online_retail.data.original
                except Exception as e:
                    self.status = "FAILED (FETCH)"
                    logger.error(f"Fatal error during fetch: {e}")
                    return None

            # PHASE 1: Explore & Validate
            mapping, missing = auto_detect_columns(df_raw)
            if not mapping:
                self.status = f"FAILED (VALIDATION: Missing {missing})"
                logger.error(f"Processing halted: {self.status}")
                return None

            # PHASE 2: Transform
            self.status = "PHASE 2: TRANSFORM"
            logger.info("Starting transformation phase...")
            
            df = df_raw.rename(columns={v: k for k, v in mapping.items()})
            
            df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
            df = df.dropna(subset=['InvoiceDate'])
            
            df = df.dropna(subset=['CustomerID'])
            df['CustomerID'] = df['CustomerID'].astype(float).astype(int).astype(str)
            
            df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
            df['is_return'] = df['InvoiceNo'].apply(lambda x: str(x).startswith('C')) | (df['Quantity'] < 0)
            
            df['DayOfWeek'] = df['InvoiceDate'].dt.dayofweek
            df['MonthStr'] = df['InvoiceDate'].dt.to_period('M').astype(str)
            df['Year'] = df['InvoiceDate'].dt.year

            # PHASE 3: Load
            self.status = "PHASE 3: LOAD"
            self.df = df
            
            if not os.path.exists(CACHE_FILE):
                logger.info("Saving cleaned data to cache...")
                df.to_parquet(CACHE_FILE)
            
            self.status = "OK"
            logger.info(f"ETL COMPLETED SUCCESSFULY. Final shape: {df.shape}")
            return self.df

        except Exception as e:
            self.status = f"FAILED (TRANSFORM: {str(e)})"
            logger.error(f"Transformation crash: {e}")
            return None
        finally:
            self._is_loading = False

    def get_data(self):
        if self.df is None and "FAILED" not in self.status:
            return self.load_data()
        return self.df

data_provider = DataProvider.get_instance()
