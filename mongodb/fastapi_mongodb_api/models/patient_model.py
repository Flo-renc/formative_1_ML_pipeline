from pydantic import BaseModel, Field
from datetime import datetime

class Patient(BaseModel):
    age: int = Field(..., gt=0, description="Age must be greater than zero")
    sex: str = Field(..., pattern="^(male|female)$")
    trestbps: int = Field(..., gt=0, description="Resting BP must be positive")
    chol: int = Field(..., gt=0, description="Cholesterol must be positive")
    fbs: str = Field(..., pattern="^(true|false)$")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
