from fastapi import APIRouter, HTTPException
from models.symptom_model import ClinicalSymptom
from config.db import get_db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/symptoms/")
def create_symptom(symptom: ClinicalSymptom):
    db = get_db()
    symptoms = db["clinical_symptoms"]
    symptom_dict = symptom.dict()
    result = symptoms.insert_one(symptom_dict)
    return {"id": str(result.inserted_id)}

@router.get("/symptoms/")
def get_all_symptoms():
    db = get_db()
    symptoms = db["clinical_symptoms"]
    result = []
    for s in symptoms.find():
        # Convert all ObjectId fields to strings
        s["_id"] = str(s["_id"])
        if "patient_id" in s:
            s["patient_id"] = str(s["patient_id"])
        result.append(s)
    return result

@router.get("/symptoms/{id}")
def get_symptom(id: str):
    db = get_db()
    symptoms = db["clinical_symptoms"]
    symptom = symptoms.find_one({"_id": ObjectId(id)})
    if not symptom:
        raise HTTPException(status_code=404, detail="Symptom not found")
    # Convert ObjectIds to strings
    symptom["_id"] = str(symptom["_id"])
    if "patient_id" in symptom:
        symptom["patient_id"] = str(symptom["patient_id"])
    return symptom

@router.put("/symptoms/{id}")
def update_symptom(id: str, data: dict):
    db = get_db()
    symptoms = db["clinical_symptoms"]
    data["updated_at"] = datetime.utcnow()
    result = symptoms.update_one({"_id": ObjectId(id)}, {"$set": data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Symptom not found or no update made")
    return {"message": "Symptom updated successfully"}

@router.delete("/symptoms/{id}")
def delete_symptom(id: str):
    db = get_db()
    symptoms = db["clinical_symptoms"]
    result = symptoms.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Symptom not found")
    return {"message": "Symptom deleted successfully"}
