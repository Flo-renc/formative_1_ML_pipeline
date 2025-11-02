#!/usr/bin/env python3
"""
Enhanced ML Prediction Script for Heart Disease Classification
Integrates with MySQL Database and API for complete pipeline
"""

import json
import numpy as np
import pandas as pd
import requests
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os
import pymysql
from datetime import datetime
from dotenv import load_dotenv
# Add MongoDB imports
from pymongo import MongoClient
from bson import ObjectId

# Load environment variables
load_dotenv()

class HeartDiseasePredictionPipeline:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.api_base_url = "http://localhost:8000"
        self.model_file = "heart_disease_model.pkl"
        self.scaler_file = "scaler.pkl"
        # MongoDB connection
        self.mongo_client = None
        self.mongo_db = None
    
    def get_mysql_connection(self):
        """Get MySQL database connection"""
        try:
            connection = pymysql.connect(
                host=os.getenv('MYSQL_HOST', 'localhost'),
                user=os.getenv('MYSQL_USER', 'root'),
                password=os.getenv('MYSQL_PASSWORD', ''),
                database=os.getenv('MYSQL_DATABASE', 'heart_disease_db'),
                port=int(os.getenv('MYSQL_PORT', 3306)),
                cursorclass=pymysql.cursors.DictCursor
            )
            return connection
        except Exception as e:
            print(f'Failed to connect to MySQL: {e}')
            return None
    
    def get_mongodb_connection(self):
        """Get MongoDB database connection"""
        try:
            self.mongo_client = MongoClient('mongodb://localhost:27017/')
            self.mongo_db = self.mongo_client.heart_disease_db
            # Test connection
            self.mongo_client.admin.command('ping')
            print("MongoDB connection successful")
            return True
        except Exception as e:
            print(f'Failed to connect to MongoDB: {e}')
            return False
    
    def load_or_create_model(self):
        """Load existing model or create and train a new one"""
        if os.path.exists(self.model_file) and os.path.exists(self.scaler_file):
            print("Loading existing trained model...")
            with open(self.model_file, 'rb') as f:
                self.model = pickle.load(f)
            with open(self.scaler_file, 'rb') as f:
                self.scaler = pickle.load(f)
        else:
            print("Creating and training new model...")
            self.create_and_train_model()
    
    def create_and_train_model(self):
        """Create and train a heart disease prediction model using Cleveland dataset"""
        # Enhanced training data (Cleveland Heart Disease Dataset format)
        training_data = [
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
            [69, 0, 3, 140, 239, 0, 1, 151, 0, 1.8, 2, 2, 2, 1],
            [45, 1, 1, 110, 264, 0, 1, 132, 0, 1.2, 1, 0, 3, 1],
            [68, 1, 0, 144, 193, 1, 1, 141, 0, 3.4, 1, 2, 3, 1],
            [57, 1, 0, 130, 131, 0, 1, 115, 1, 1.2, 1, 1, 3, 1],
            [57, 0, 1, 130, 236, 0, 0, 174, 0, 0.0, 1, 1, 2, 1]
        ]
        
        columns = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 
                   'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target']
        
        df = pd.DataFrame(training_data, columns=columns)
        
        # Prepare features and target
        X = df.drop('target', axis=1)
        y = df['target']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Model trained with accuracy: {accuracy:.2%}")
        
        # Save model and scaler
        with open(self.model_file, 'wb') as f:
            pickle.dump(self.model, f)
        with open(self.scaler_file, 'wb') as f:
            pickle.dump(self.scaler, f)
    
    def fetch_latest_patient_from_api(self):
        """Fetch the latest patient record from FastAPI"""
        try:
            print("Fetching latest patient data from API...")
            response = requests.get(f"{self.api_base_url}/mysql/patients")
            
            if response.status_code == 200:
                patients = response.json()
                if patients:
                    latest_patient = patients[-1]  # Get the last patient
                    print(f"Latest patient fetched: ID {latest_patient[0]}")
                    return latest_patient
                else:
                    print("No patients found in database")
                    return None
            else:
                print(f"API request failed with status code: {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("Could not connect to API. Make sure the FastAPI server is running.")
            return None
        except Exception as e:
            print(f"Error fetching data from API: {e}")
            return None
    
    def prepare_features_for_prediction(self, patient_data):
        """Convert patient data to ML model format"""
        try:
            # Patient data format from API:
            # [patient_id, age, sex, restbps, chol, fbs, cp, exang, oldpeak, slope, restecg, thalach, ca, thal, target]
            
            if len(patient_data) >= 14:
                features = [
                    patient_data[1],   # age
                    patient_data[2],   # sex  
                    patient_data[6],   # cp (chest pain)
                    patient_data[3],   # restbps (resting blood pressure)
                    patient_data[4],   # chol (cholesterol)
                    patient_data[5],   # fbs (fasting blood sugar)
                    patient_data[10],  # restecg (resting ECG)
                    patient_data[11],  # thalach (max heart rate)
                    patient_data[7],   # exang (exercise angina)
                    patient_data[8],   # oldpeak (ST depression)
                    patient_data[9],   # slope (ST slope)
                    patient_data[12],  # ca (major vessels)
                    patient_data[13]   # thal (thalassemia)
                ]
                
                return np.array(features).reshape(1, -1)
            else:
                print(f"Insufficient data: expected 14+ fields, got {len(patient_data)}")
                return None
                
        except Exception as e:
            print(f"Error preparing features: {e}")
            return None
    
    def make_prediction(self, features):
        """Make heart disease prediction"""
        try:
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Make prediction
            prediction = self.model.predict(features_scaled)[0]
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            # Get feature importance for interpretation
            feature_names = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 
                           'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
            
            feature_importance = dict(zip(feature_names, self.model.feature_importances_))
            
            return {
                'prediction': int(prediction),
                'probability_no_disease': float(probabilities[0]),
                'probability_disease': float(probabilities[1]),
                'confidence': float(max(probabilities)),
                'features': features.flatten().tolist(),
                'feature_importance': feature_importance
            }
            
        except Exception as e:
            print(f"Error making prediction: {e}")
            return None
    
    def log_prediction_to_database(self, patient_id, prediction_result):
        """Log prediction results to MySQL database"""
        connection = self.get_mysql_connection()
        if not connection:
            print("Cannot log prediction: Database connection failed")
            return False
        
        try:
            cursor = connection.cursor()
            
            # Create predictions table if it doesn't exist
            create_table_query = """
            CREATE TABLE IF NOT EXISTS predictions (
                prediction_id INT PRIMARY KEY AUTO_INCREMENT,
                patient_id INT NOT NULL,
                prediction_result INT NOT NULL,
                probability_no_disease DECIMAL(5,4) NOT NULL,
                probability_disease DECIMAL(5,4) NOT NULL,
                confidence_score DECIMAL(5,4) NOT NULL,
                predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                model_version VARCHAR(50) DEFAULT 'v1.0',
                FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE
            )
            """
            cursor.execute(create_table_query)
            
            # Insert prediction
            insert_query = """
            INSERT INTO predictions 
            (patient_id, prediction_result, probability_no_disease, probability_disease, confidence_score)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (
                patient_id,
                prediction_result['prediction'],
                prediction_result['probability_no_disease'],
                prediction_result['probability_disease'],
                prediction_result['confidence']
            ))
            
            connection.commit()
            prediction_id = cursor.lastrowid
            
            cursor.close()
            connection.close()
            
            print(f"Prediction logged to database with ID: {prediction_id}")
            return True
            
        except Exception as e:
            print(f"Error logging prediction to database: {e}")
            connection.rollback()
            connection.close()
            return False
    
    def log_prediction_to_mongodb(self, patient_id, prediction_result):
        """Log prediction results to MongoDB"""
        try:
            mongo_client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017'))
            db = mongo_client['heart_disease_db']
            predictions_collection = db['predictions']
            
            # Create prediction document
            prediction_doc = {
                'patient_id': patient_id,
                'prediction_result': prediction_result['prediction'],
                'probability_no_disease': prediction_result['probability_no_disease'],
                'probability_disease': prediction_result['probability_disease'],
                'confidence_score': prediction_result['confidence'],
                'predicted_at': datetime.now(),
                'model_version': 'v1.0'
            }
            
            # Insert prediction document
            result = predictions_collection.insert_one(prediction_doc)
            print(f"Prediction logged to MongoDB with ID: {result.inserted_id}")
            return True
            
        except Exception as e:
            print(f"Error logging prediction to MongoDB: {e}")
            return False
    
    def run_prediction_pipeline(self):
        """Run the complete prediction pipeline"""
        print("Starting Heart Disease Prediction Pipeline")
        print("=" * 60)
        
        # Step 1: Load model
        self.load_or_create_model()
        if not self.model or not self.scaler:
            print("Failed to load or create model")
            return
        
        # Step 2: Fetch latest patient data
        patient_data = self.fetch_latest_patient_from_api()
        if not patient_data:
            print("No patient data available")
            return
        
        patient_id = patient_data[0]
        print(f"Processing patient ID: {patient_id}")
        
        # Step 3: Prepare features
        features = self.prepare_features_for_prediction(patient_data)
        if features is None:
            print("Failed to prepare features")
            return
        
        # Step 4: Make prediction
        print("Making prediction...")
        prediction_result = self.make_prediction(features)
        if not prediction_result:
            print("Prediction failed")
            return
        
        # Step 5: Display results
        print("\n" + "=" * 60)
        print("HEART DISEASE PREDICTION RESULTS")
        print("=" * 60)
        
        diagnosis = "HEART DISEASE RISK DETECTED" if prediction_result['prediction'] == 1 else "LOW HEART DISEASE RISK"
        confidence = prediction_result['confidence'] * 100
        
        print(f"Patient ID: {patient_id}")
        print(f"Diagnosis: {diagnosis}")
        print(f"Confidence: {confidence:.1f}%")
        print(f"Disease Probability: {prediction_result['probability_disease']:.1%}")
        print(f"No Disease Probability: {prediction_result['probability_no_disease']:.1%}")
        
        # Show top risk factors
        print(f"\nTOP RISK FACTORS:")
        sorted_features = sorted(prediction_result['feature_importance'].items(), 
                               key=lambda x: x[1], reverse=True)[:5]
        for feature, importance in sorted_features:
            print(f"  - {feature}: {importance:.3f}")
        
        # Step 6: Log to database
        print(f"\nLogging results to database...")
        mysql_log_success = self.log_prediction_to_database(patient_id, prediction_result)
        mongo_log_success = self.log_prediction_to_mongodb(patient_id, prediction_result)
        
        if mysql_log_success or mongo_log_success:
            print("Results successfully logged to database")
        else:
            print("Warning: Could not log to database")
        
        # Step 7: Save to file
        result_file = f"prediction_results_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w') as f:
            json.dump({
                'patient_id': patient_id,
                'timestamp': datetime.now().isoformat(),
                'prediction_results': prediction_result,
                'raw_patient_data': patient_data
            }, f, indent=2)
        
        print(f"Results saved to: {result_file}")
        print("\nPrediction pipeline completed successfully!")

def main():
    """Main function to run the prediction pipeline"""
    pipeline = HeartDiseasePredictionPipeline()
    pipeline.run_prediction_pipeline()

if __name__ == "__main__":
    main()
