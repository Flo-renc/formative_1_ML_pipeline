import pandas as pd
from pymongo import MongoClient
from bson import ObjectId

# MongoDB Connectio
client = MongoClient("mongodb+srv://team_user:user12345@cluster0.akwkdkn.mongodb.net/heart_disease_db?retryWrites=true&w=majority&appName=heart_disease_db")
db = client["heart_disease_db"]

# Collections ---
patients_col = db["patients"]
symptoms_col = db["clinical_symptoms"]
tests_col = db["cardiac_tests"]

df = pd.read_csv("heart_cleveland_upload.csv")
df.columns = df.columns.str.strip().str.lower()

cp_map = {
    0: "typical angina",
    1: "atypical angina",
    2: "non-anginal pain",
    3: "asymptomatic"
}
restecg_map = {
    0: "normal",
    1: "ST-T abnormality",
    2: "LV hypertrophy"
}
slope_map = {
    0: "upsloping",
    1: "flat",
    2: "downsloping"
}
thal_map = {
    0: "normal",
    1: "fixed defect",
    2: "reversible defect"
}

# Apply mappings
df["sex"] = df["sex"].map({1: "male", 0: "female"})
df["fbs"] = df["fbs"].map({1: "true", 0: "false"})
df["exang"] = df["exang"].map({1: "yes", 0: "no"})
df["cp"] = df["cp"].map(cp_map)
df["restecg"] = df["restecg"].map(restecg_map)
df["slope"] = df["slope"].map(slope_map)
df["thal"] = df["thal"].map(thal_map)
df["condition"] = df["condition"].map({1: "disease", 0: "no disease"})


for _, row in df.iterrows():
    # Patients
    patient_doc = {
        "age": int(row["age"]),
        "sex": row["sex"],
        "trestbps": int(row["trestbps"]),
        "chol": int(row["chol"]),
        "fbs": row["fbs"]
    }
    inserted_id = patients_col.insert_one(patient_doc).inserted_id

    # Clinical Symptoms
    symptom_doc = {
        "patient_id": inserted_id,
        "cp": row["cp"],
        "exang": row["exang"],
        "oldpeak": float(row["oldpeak"]),
        "slope": row["slope"]
    }
    symptoms_col.insert_one(symptom_doc)

    # Cardiac Tests
    test_doc = {
        "patient_id": inserted_id,
        "restecg": row["restecg"],
        "thalach": int(row["thalach"]),
        "ca": int(row["ca"]),
        "thal": row["thal"],
        "target": row["condition"]
    }
    tests_col.insert_one(test_doc)

print("✅ Cleaned data successfully inserted into MongoDB!")
