import os
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


CSV_NAME = "heart_cleveland_upload.csv"
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV_PATH = os.path.join(PROJECT_ROOT, CSV_NAME)

if not os.path.isfile(CSV_PATH):
    raise FileNotFoundError(
        f"\nCSV not found!\n"
        f"   Expected: {CSV_PATH}\n"
        f"   • Put '{CSV_NAME}' in the project root folder.\n"
        f"   • Current folder tree:\n"
        f"       {PROJECT_ROOT}\n"
    )

print(f"Loading dataset from: {CSV_PATH}")
df = pd.read_csv(CSV_PATH)
print(f"Dataset loaded: {df.shape[0]} samples, {df.shape[1]} features")


X = df.drop(columns=["condition"])
y = df["condition"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)


scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train Logistic Regression

model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train_scaled, y_train)

y_pred = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nAccuracy: {accuracy:.3f}")
print(classification_report(y_test, y_pred))

# Save model + scaler

MODEL_PATH   = os.path.join(os.path.dirname(__file__), "heart_disease_model.pkl")
SCALER_PATH  = os.path.join(os.path.dirname(__file__), "scaler.pkl")

with open(MODEL_PATH, "wb") as f:
    pickle.dump(model, f)
with open(SCALER_PATH, "wb") as f:
    pickle.dump(scaler, f)

print(f"\nModel   → {MODEL_PATH}")
print(f"Scaler  → {SCALER_PATH}")