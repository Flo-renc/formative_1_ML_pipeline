from fastapi import APIRouter, HTTPException
from models.symptom_model import ClinicalSymptom
from config.db import db
from bson import ObjectId

router = APIRouter()
symptoms = db["clinical_symptoms"]

@router.post("/symptoms/")
def create_symptom(symptom: ClinicalSymptom):
    result = symptoms.insert_one(symptom.dict())
    return {"id": str(result.inserted_id)}

@router.get("/symptoms/{id}")
def get_symptom(id: str):
    symptom = symptoms.find_one({"_id": ObjectId(id)})
    if not symptom:
        raise HTTPException(404, "Symptom not found")
    symptom["_id"] = str(symptom["_id"])
    return symptom

@router.put("/symptoms/{id}")
def update_symptom(id: str, data: dict):
    result = symptoms.update_one({"_id": ObjectId(id)}, {"$set": data})
    return {"updated_count": result.modified_count}

@router.delete("/symptoms/{id}")
def delete_symptom(id: str):
    result = symptoms.delete_one({"_id": ObjectId(id)})
    return {"deleted_count": result.deleted_count}
