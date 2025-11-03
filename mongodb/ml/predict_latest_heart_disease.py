import requests
import pandas as pd
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from bson import ObjectId

# API base URL
BASE_URL = "http://127.0.0.1:8000"

# Reverse mappings from string to numerical values based on the data loading script
sex_map = {"male": 1, "female": 0}
fbs_map = {"true": 1, "false": 0}
exang_map = {"yes": 1, "no": 0}
cp_map_rev = {
    "typical angina": 0,
    "atypical angina": 1,
    "non-anginal pain": 2,
    "asymptomatic": 3
}
restecg_map_rev = {
    "normal": 0,
    "ST-T wave abnormality": 1,
    "left ventricular hypertrophy": 2
}
slope_map_rev = {
    "upsloping": 0,
    "flat": 1,
    "downsloping": 2
}
thal_map_rev = {
    "normal": 0,
    "fixed defect": 1,
    "reversible defect": 2
}
condition_map_rev = {
    "no disease": 0,
    "disease": 1
}

# Fetch all tests
tests_response = requests.get(f"{BASE_URL}/tests/")
tests = tests_response.json()

# Fetch all symptoms
symptoms_response = requests.get(f"{BASE_URL}/symptoms/")
all_symptoms = symptoms_response.json()

# Build a list of complete entries
data = []
for test in tests:
    patient_id = test["patient_id"]  # Use patient_id here
    
    # Fetch patient by ID
    patient_response = requests.get(f"{BASE_URL}/patients/{patient_id}")
    if patient_response.status_code != 200:
        continue  # Skip if patient not found
    patient = patient_response.json()
    
    # Find matching symptom by patient_id
    matching_symptoms = [s for s in all_symptoms if s["patient_id"] == patient_id]
    if not matching_symptoms:
        continue  # Skip if no symptom found
    symptom = matching_symptoms[0]
    
    # Build row
    row = {
        "age": patient["age"],
        "sex": patient["sex"],
        "cp": symptom["cp"],
        "trestbps": patient["trestbps"],
        "chol": patient["chol"],
        "fbs": patient["fbs"],
        "restecg": test["restecg"],
        "thalach": test["thalach"],
        "exang": symptom["exang"],
        "oldpeak": symptom["oldpeak"],
        "slope": symptom["slope"],
        "ca": test["ca"],
        "thal": test["thal"],
        "condition": test["target"],
        "created_at": patient.get("created_at", str(ObjectId(test["_id"]).generation_time)) }
    data.append(row)

# Sort data by created_at ascending
data.sort(key=lambda x: datetime.fromisoformat(x["created_at"]))

# Create DataFrame
df = pd.DataFrame(data)

# Apply reverse mappings to convert strings to numerical values
df["sex"] = df["sex"].map(sex_map)
df["fbs"] = df["fbs"].map(fbs_map)
df["cp"] = df["cp"].map(cp_map_rev)
df["restecg"] = df["restecg"].map(restecg_map_rev)
df["exang"] = df["exang"].map(exang_map)
df["slope"] = df["slope"].map(slope_map_rev)
df["thal"] = df["thal"].map(thal_map_rev)
df["condition"] = df["condition"].map(condition_map_rev)

# Prepare features and target
feature_columns = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal"
]
X = df[feature_columns]
y = df["condition"]

# Use all but the last entry for training
X_train = X.iloc[:-1]
y_train = y.iloc[:-1]

# Latest entry for prediction
X_latest = X.iloc[-1:]

# Train a simple Logistic Regression model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Make prediction
prediction = model.predict(X_latest)[0]

# For comparison, get actual value 
actual = y.iloc[-1]

print(f"Predicted condition (0: no disease, 1: disease): {prediction}")
print(f"Actual condition: {actual}")