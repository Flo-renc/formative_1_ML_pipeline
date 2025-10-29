from fastapi import FastAPI
from routes.patient_routes import router as patient_router
from routes.symptom_routes import router as symptom_router
from routes.test_routes import router as test_router

app = FastAPI(title="Heart Disease MongoDB API")

# Include routes
app.include_router(patient_router, tags=["Patients"])
app.include_router(symptom_router, tags=["Symptoms"])
app.include_router(test_router, tags=["Cardiac Tests"])

@app.get("/")
def home():
    return {"message": "Heart Disease MongoDB API is running"}
