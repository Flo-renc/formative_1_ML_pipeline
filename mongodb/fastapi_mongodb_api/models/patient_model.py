from pydantic import BaseModel, Field
from typing import Optional

class Patient(BaseModel):
    age: int = Field(..., gt=0, description="Age must be positive")
    sex: str
    trestbps: int
    chol: int
    fbs: str
