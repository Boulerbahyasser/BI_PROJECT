from fastapi import FastAPI
from .data_provider import data_provider
from .api.endpoints import router as api_router
from fastapi.middleware.cors import CORSMiddleware
import threading

app = FastAPI(title="Predictive BI E-commerce Platform API")

# Enable CORS for Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    # Load data in a background thread
    thread = threading.Thread(target=data_provider.load_data)
    thread.daemon = True
    thread.start()
    print("🚀 Background data loading started...")

@app.get("/")
def home():
    return {"status": "online", "message": "Predictive BI API", "etl_status": data_provider.status}

# Include modular API routes
app.include_router(api_router, prefix="/api/v1")
