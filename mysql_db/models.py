from pydantic import BaseModel, Field
from typing import Optional

class PatientBase(BaseModel):
    age: int = Field(..., ge=1, le=120, description="Age in years")
    sex: int = Field(..., ge=0, le=1, description="1: male, 0: female")
    restbps: int = Field(..., ge=80, le=200, description="Resting blood pressure")
    chol: int = Field(..., ge=100, le=600, description='Serum cholesterol')
    fbs: int = Field(..., ge=0, le=1, description='Fasting blood sugar > 120 mg/dl')

class ClinicalSymptomsBase(BaseModel):
    cp: int = Field(..., ge=0, le=3, description="Chest pain type")
    exang: int = Field(..., ge=0, le=1, description="Exercise induced angina")
    oldpeak: float = Field(..., ge=0, le=10, description="ST depression")
    slope: int = Field(..., ge=0, le=2, description="Slope of peak exercise ST segment")
    
class CardiacTestsBase(BaseModel):
    restecg: int = Field(..., ge=0, le=2, description="Resting ECG results")
    thalach: int = Field(..., ge=60, le=220, description="Max heart rate")
    ca: int = Field(..., ge=0, le=3, description="Number of major vessels")
    thal: int = Field(..., ge=1, le=3, description="Thalassemia")
    target: int = Field(..., ge=0, le=1, description="Heart disease diagnosis")

class CompletePatientRecord(BaseModel):
    patient: PatientBase
    symptoms: ClinicalSymptomsBase
    tests: CardiacTestsBase

class PatientResponse(PatientBase):
    patient_id: int

class CompletePatientResponse(BaseModel):
    patient_id: int
    patient: PatientBase
    symptoms: ClinicalSymptomsBase
    tests: CardiacTestsBase