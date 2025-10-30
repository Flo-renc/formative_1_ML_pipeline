from pydantic import BaseModel, Field, constr, conint
from datetime import datetime

class CardiacTest(BaseModel):
    patient_id: constr(min_length=1) = Field(..., description="Unique ID of the patient")

    restecg: constr(
        pattern="^(normal|ST-T wave abnormality|left ventricular hypertrophy)$"
    ) = Field(..., description="Resting electrocardiographic results")

    thalach: conint(gt=0, le=250) = Field(
        ..., description="Maximum heart rate achieved (0–250 bpm)"
    )

    ca: conint(ge=0, le=3) = Field(
        ..., description="Number of major vessels (0–3) colored by fluoroscopy"
    )

    thal: constr(pattern="^(normal|fixed defect|reversible defect)$") = Field(
        ..., description="Thalassemia type"
    )

    target: constr(pattern="^(disease|no disease)$") = Field(
        ..., description="Heart disease diagnosis result"
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
