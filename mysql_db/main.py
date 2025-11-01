from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import mysql_routes

# Create FastAPI app
app = FastAPI(
    title="Heart Disease Prediction API",
    description="API for managing heart disease patient data in MySQL",
    version="1.0.0"
)

# Configure CORS (allows frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include MySQL router
app.include_router(mysql_routes.router)

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to Heart Disease Prediction API",
        "endpoints": {
            "MySQL CRUD": "/mysql/patients",
            "Documentation": "/docs",
            "Alternative Documentation": "/redoc"
        }
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Heart Disease API",
        "database": "MySQL"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)