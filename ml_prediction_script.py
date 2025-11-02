#!/usr/bin/env python3
"""
ML Prediction Script for Heart Disease Classification
Task 3: Load model and make predictions using the latest entry data
"""

import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

def load_or_create_model():
    """Load existing model or create and train a new one"""
    model_file = "heart_disease_model.pkl"
    scaler_file = "scaler.pkl"
    
    if os.path.exists(model_file) and os.path.exists(scaler_file):
        print("Loading existing trained model...")
        with open(model_file, 'rb') as f:
            model = pickle.load(f)
        with open(scaler_file, 'rb') as f:
            scaler = pickle.load(f)
        return model, scaler
    else:
        print("Creating and training new model...")
        return create_and_train_model()

def create_and_train_model():
    """Create and train a heart disease prediction model"""
    # Sample heart disease data (Cleveland dataset format)
    # Features: age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal
    # Target: 0 = no disease, 1 = disease
    
    sample_data = [
        [63, 1, 3, 145, 233, 1, 0, 150, 0, 2.3, 0, 0, 1, 1],
        [37, 1, 2, 130, 250, 0, 1, 187, 0, 3.5, 0, 0, 2, 1],
        [41, 0, 1, 130, 204, 0, 0, 172, 0, 1.4, 2, 0, 2, 0],
        [56, 1, 1, 120, 236, 0, 1, 178, 0, 0.8, 2, 0, 2, 0],
        [57, 0, 0, 120, 354, 0, 1, 163, 1, 0.6, 2, 0, 2, 1],
        [57, 1, 0, 140, 192, 0, 1, 148, 0, 0.4, 1, 0, 1, 0],
        [56, 0, 1, 140, 294, 0, 0, 153, 0, 1.3, 1, 0, 2, 0],
        [44, 1, 1, 120, 263, 0, 1, 173, 0, 0.0, 2, 0, 3, 0],
        [52, 1, 2, 172, 199, 1, 1, 162, 0, 0.5, 2, 0, 3, 0],
        [57, 1, 2, 150, 168, 0, 1, 174, 0, 1.6, 2, 0, 2, 0],
        [54, 1, 0, 140, 239, 0, 1, 160, 0, 1.2, 2, 0, 2, 0],
        [48, 0, 2, 130, 275, 0, 1, 139, 0, 0.2, 2, 0, 2, 0],
        [49, 1, 1, 130, 266, 0, 1, 171, 0, 0.6, 2, 0, 2, 0],
        [64, 1, 3, 110, 211, 0, 0, 144, 1, 1.8, 1, 0, 2, 1],
        [58, 0, 3, 150, 283, 1, 0, 162, 0, 1.0, 2, 0, 2, 1],
        [50, 0, 2, 120, 219, 0, 1, 158, 0, 1.6, 1, 0, 2, 0],
        [58, 0, 2, 120, 340, 0, 1, 172, 0, 0.0, 2, 0, 2, 0],
        [66, 0, 3, 150, 226, 0, 1, 114, 0, 2.6, 0, 0, 2, 1],
        [43, 1, 0, 150, 247, 0, 1, 171, 0, 1.5, 2, 0, 2, 0],
        [69, 0, 3, 140, 239, 0, 1, 151, 0, 1.8, 2, 2, 2, 1]
    ]
    
    columns = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 
               'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target']
    
    df = pd.DataFrame(sample_data, columns=columns)
    
    # Prepare features and target
    X = df.drop('target', axis=1)
    y = df['target']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model trained with accuracy: {accuracy:.2f}")
    
    # Save model and scaler
    with open("heart_disease_model.pkl", 'wb') as f:
        pickle.dump(model, f)
    with open("scaler.pkl", 'wb') as f:
        pickle.dump(scaler, f)
    
    return model, scaler

def load_latest_entry():
    """Load the latest patient entry from the API data"""
    try:
        with open('latest_entry.json', 'r') as f:
            latest_entry = json.load(f)
        return latest_entry
    except FileNotFoundError:
        print("latest_entry.json not found. Run Bash.sh first to fetch data.")
        return None
    except json.JSONDecodeError:
        print("Invalid JSON in latest_entry.json")
        return None

def prepare_features_for_prediction(entry_data):
    """Convert API entry data to ML features"""
    try:
        if isinstance(entry_data, list) and len(entry_data) >= 14:
            # Entry is in array format [patient_id, age, sex, trestbps, chol, fbs, cp, exang, oldpeak, slope, restecg, thalach, ca, thal, target]
            features = [
                entry_data[1],   # age
                entry_data[2],   # sex
                entry_data[6],   # cp
                entry_data[3],   # trestbps
                entry_data[4],   # chol
                entry_data[5],   # fbs
                entry_data[10],  # restecg
                entry_data[11],  # thalach
                entry_data[7],   # exang
                entry_data[8],   # oldpeak
                entry_data[9],   # slope
                entry_data[12],  # ca
                entry_data[13]   # thal
            ]
        else:
            print("Unexpected data format")
            return None
            
        return np.array(features).reshape(1, -1)
    
    except Exception as e:
        print(f"Error preparing features: {e}")
        return None

def make_prediction(model, scaler, features):
    """Make heart disease prediction"""
    try:
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Make prediction
        prediction = model.predict(features_scaled)[0]
        probability = model.predict_proba(features_scaled)[0]
        
        return prediction, probability
    
    except Exception as e:
        print(f"Error making prediction: {e}")
        return None, None

def main():
    """Main function to run the ML prediction pipeline"""
    print("Starting Heart Disease Prediction Pipeline...")
    print("=" * 50)
    
    # Step 1: Load or create model
    model, scaler = load_or_create_model()
    
    # Step 2: Load latest entry data
    print("\nLoading latest patient entry...")
    latest_entry = load_latest_entry()
    
    if latest_entry is None:
        print("Cannot proceed without patient data.")
        return
    
    print("Latest entry loaded successfully")
    print(f"Raw data: {latest_entry}")
    
    # Step 3: Prepare data for prediction
    print("\nPreparing features for ML model...")
    features = prepare_features_for_prediction(latest_entry)
    
    if features is None:
        print("Failed to prepare features for prediction.")
        return
    
    print(f"Features prepared: {features.flatten()}")
    
    # Step 4: Make prediction
    print("\nMaking heart disease prediction...")
    prediction, probability = make_prediction(model, scaler, features)
    
    if prediction is None:
        print("Failed to make prediction.")
        return
    
    # Step 5: Display results
    print("\n" + "=" * 50)
    print("HEART DISEASE PREDICTION RESULTS")
    print("=" * 50)
    
    diagnosis = "HEART DISEASE DETECTED" if prediction == 1 else "NO HEART DISEASE"
    confidence = max(probability) * 100
    
    print(f"Patient Data: {features.flatten()}")
    print(f"Prediction: {diagnosis}")
    print(f"Confidence: {confidence:.1f}%")
    print(f"Probability [No Disease, Disease]: [{probability[0]:.3f}, {probability[1]:.3f}]")
    
    # Save results
    results = {
        "features": features.flatten().tolist(),
        "prediction": int(prediction),
        "diagnosis": diagnosis,
        "confidence": float(confidence),
        "probability": probability.tolist()
    }
    
    with open("prediction_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("Results saved to prediction_results.json")
    print("\nPrediction pipeline completed successfully!")

if __name__ == "__main__":
    main()
