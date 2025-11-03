from fastapi import APIRouter, HTTPException
from config.db import get_db
import pickle
import numpy as np
import os

router = APIRouter()

MODEL_PATH = r"C:\Users\fadhl\OneDrive\Desktop\heart_disease_project\model.pkl"
SCALER_PATH = r"C:\Users\fadhl\OneDrive\Desktop\heart_disease_project\scaler.pkl"

if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
    raise RuntimeError("Model or scaler not found. Please train the model first.")

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)
with open(SCALER_PATH, "rb") as f:
    scaler = pickle.load(f)

@router.post("/predict/latest/")
def predict_latest_patient():
    """
    Predict heart disease for the latest patient in the database.
    """
    db = get_db()

    # Get the latest patient inserted
    patient = db["patients"].find_one(sort=[("_id", -1)])
    if not patient:
        raise HTTPException(status_code=404, detail="No patients found in database")

    patient_id = patient["_id"]

    # Fetch related symptoms
    symptom = db["clinical_symptoms"].find_one({"patient_id": patient_id})
    if not symptom:
        raise HTTPException(status_code=404, detail="Clinical symptoms not found")

    # Fetch related cardiac test
    test = db["cardiac_tests"].find_one({"patient_id": patient_id})
    if not test:
        raise HTTPException(status_code=404, detail="Cardiac test not found")

    # Prepare feature vector
    X = np.array([[patient["age"],
                   1 if patient["sex"] == "male" else 0,
                   ["typical angina", "atypical angina", "non-anginal pain", "asymptomatic"].index(symptom["cp"]),
                   patient["trestbps"],
                   patient["chol"],
                   1 if patient["fbs"] == "true" else 0,
                   ["normal", "ST-T abnormality", "LV hypertrophy"].index(test["restecg"]),
                   test["thalach"],
                   1 if symptom["exang"] == "yes" else 0,
                   symptom["oldpeak"],
                   ["upsloping", "flat", "downsloping"].index(symptom["slope"]),
                   test["ca"],
                   ["normal", "fixed defect", "reversible defect"].index(test["thal"])
                   ]])

    # Scale and predict
    X_scaled = scaler.transform(X)
    prediction = model.predict(X_scaled)[0]
    pred_label = "disease" if prediction == 1 else "no disease"

    return {"patient_id": str(patient_id), "prediction": pred_label}
