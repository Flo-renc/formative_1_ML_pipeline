from fastapi import APIRouter, HTTPException
from models.patient_model import Patient
from config.db import get_db
from bson import ObjectId
from datetime import datetime
from typing import List

router = APIRouter()

@router.post("/patients/")
def create_patient(patient: Patient):
    db = get_db()
    patients = db["patients"]
    patient_dict = patient.dict()
    result = patients.insert_one(patient_dict)
    return {"id": str(result.inserted_id)}

@router.get("/patients/{id}")
def get_patient(id: str):
    db = get_db()
    patients = db["patients"]
    patient = patients.find_one({"_id": ObjectId(id)})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    patient["_id"] = str(patient["_id"])
    return patient

@router.get("/patients/", response_model=List[Patient])
def get_all_patients():
    db = get_db()
    patients = list(db.patients.find())
    for p in patients:
        p["id"] = str(p["_id"])
        p.pop("_id", None)
    return patients

@router.put("/patients/{id}")
def update_patient(id: str, data: dict):
    db = get_db()
    patients = db["patients"]
    data["updated_at"] = datetime.utcnow()
    result = patients.update_one({"_id": ObjectId(id)}, {"$set": data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found or no changes made")
    return {"message": "Patient updated successfully"}

@router.delete("/patients/{id}")
def delete_patient(id: str):
    db = get_db()
    patients = db["patients"]
    result = patients.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient deleted successfully"}
