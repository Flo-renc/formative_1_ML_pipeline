from pydantic import BaseModel, Field
from typing import Optional

class ClinicalSymptom(BaseModel):
    patient_id: str
    cp: str
    exang: str
    oldpeak: float
    slope: str
