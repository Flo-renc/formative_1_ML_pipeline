from pydantic import BaseModel
from typing import Optional

class CardiacTest(BaseModel):
    patient_id: str
    restecg: str
    thalach: int
    ca: int
    thal: str
    target: str
