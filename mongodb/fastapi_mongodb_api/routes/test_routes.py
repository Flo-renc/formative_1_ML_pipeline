from fastapi import APIRouter, HTTPException
from models.test_model import CardiacTest
from config.db import db
from bson import ObjectId

router = APIRouter()
tests = db["cardiac_tests"]

@router.post("/tests/")
def create_test(test: CardiacTest):
    result = tests.insert_one(test.dict())
    return {"id": str(result.inserted_id)}

@router.get("/tests/{id}")
def get_test(id: str):
    test = tests.find_one({"_id": ObjectId(id)})
    if not test:
        raise HTTPException(404, "Test not found")
    test["_id"] = str(test["_id"])
    return test

@router.put("/tests/{id}")
def update_test(id: str, data: dict):
    result = tests.update_one({"_id": ObjectId(id)}, {"$set": data})
    return {"updated_count": result.modified_count}

@router.delete("/tests/{id}")
def delete_test(id: str):
    result = tests.delete_one({"_id": ObjectId(id)})
    return {"deleted_count": result.deleted_count}
