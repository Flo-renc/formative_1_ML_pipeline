from fastapi import APIRouter, HTTPException, Body
from models.test_model import CardiacTest
from config.db import get_db
from bson import ObjectId
from datetime import datetime

router = APIRouter()
collection_name = "cardiac_tests"

@router.post("/tests/", status_code=201)
def create_test(test: CardiacTest):
    db = get_db()
    tests = db[collection_name]
    test_dict = test.dict()
    result = tests.insert_one(test_dict)
    return {"id": str(result.inserted_id), "message": "Test record created successfully"}

@router.get("/tests/")
def get_all_tests():
    """
    Get all cardiac test records.
    """
    db = get_db()
    tests = db[collection_name]
    result = []
    for t in tests.find():
        t["_id"] = str(t["_id"])  # convert ObjectId
        if "patient_id" in t:
            t["patient_id"] = str(t["patient_id"])  # convert foreign key ObjectId
        result.append(t)
    return result

@router.get("/tests/{id}")
def get_test(id: str):
    db = get_db()
    tests = db[collection_name]

    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    test = tests.find_one({"_id": ObjectId(id)})
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    # Convert ObjectId fields
    test["_id"] = str(test["_id"])
    if "patient_id" in test:
        test["patient_id"] = str(test["patient_id"])

    return test

@router.put("/tests/{id}")
def update_test(id: str, data: dict = Body(...)):
    db = get_db()
    tests = db[collection_name]

    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    data["updated_at"] = datetime.utcnow()
    result = tests.update_one({"_id": ObjectId(id)}, {"$set": data})

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Test not found or no update made")

    return {"message": "Test updated successfully"}

@router.delete("/tests/{id}")
def delete_test(id: str):
    db = get_db()
    tests = db[collection_name]

    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    result = tests.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Test not found")

    return {"message": "Test deleted successfully"}
