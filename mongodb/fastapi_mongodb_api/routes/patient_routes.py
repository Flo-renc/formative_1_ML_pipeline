from fastapi import APIRouter, HTTPException
from models.patient_model import Patient
from config.db import db
from bson import ObjectId

router = APIRouter()
patients = db["patients"]

@router.post("/patients/")
def create_patient(patient: Patient):
    result = patients.insert_one(patient.dict())
    return {"id": str(result.inserted_id)}

@router.get("/patients/{id}")
def get_patient(id: str):
    patient = patients.find_one({"_id": ObjectId(id)})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient["_id"] = str(patient["_id"])
    return patient

@router.get("/patients/")
def get_all_patients():
    all_patients = []
    for p in patients.find():
        p["_id"] = str(p["_id"])
        all_patients.append(p)
    return all_patients

@router.put("/patients/{id}")
def update_patient(id: str, data: dict):
    result = patients.update_one({"_id": ObjectId(id)}, {"$set": data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found or no changes made")
    return {"message": "Patient updated"}

@router.delete("/patients/{id}")
def delete_patient(id: str):
    result = patients.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient deleted"}
