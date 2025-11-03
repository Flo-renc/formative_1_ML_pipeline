from pydantic import BaseModel, Field

class PredictionInput(BaseModel):
    age: int = Field(..., gt=0)
    sex: str = Field(..., pattern="^(male|female)$")
    cp: str = Field(..., description="Chest pain type")
    trestbps: int = Field(..., gt=0)
    chol: int = Field(..., gt=0)
    fbs: str = Field(..., pattern="^(true|false)$")
    restecg: str = Field(..., description="Resting ECG results")
    thalach: int = Field(..., gt=0)
    exang: str = Field(..., pattern="^(yes|no)$")
    oldpeak: float = Field(..., ge=0)
    slope: str = Field(..., description="Slope of the peak exercise ST segment")
    ca: int = Field(..., ge=0, le=3)
    thal: str = Field(..., description="Thalassemia type")
