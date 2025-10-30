from pydantic import BaseModel, Field
from datetime import datetime

class ClinicalSymptom(BaseModel):
    patient_id: str
    cp: str = Field(..., description="Chest pain type (e.g., typical angina, atypical angina, non-anginal pain, asymptomatic)")
    exang: str = Field(..., description="Exercise induced angina (yes/no)")
    oldpeak: float = Field(..., ge=0, description="ST depression induced by exercise relative to rest")
    slope: str = Field(..., description="Slope of the peak exercise ST segment (upsloping, flat, downsloping)")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
