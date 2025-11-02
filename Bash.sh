#!/usr/bin/env bash

# Step 1: Fetch Data for Prediction
echo -e "\e[34m[INFO] Fetching data Using the FastAPI MySQL Database...\e[0m"

# FastAPI MySQL API base URL (assuming server is running on localhost:8000)
BASE_URL="http://localhost:8000"

# Function to check if API is available
check_api() {
    echo -e "\e[33m[INFO] Checking if FastAPI MySQL server is running...\e[0m"
    if curl -s --fail "${BASE_URL}/health" > /dev/null; then
        echo -e "\e[32m[SUCCESS] FastAPI MySQL server is running!\e[0m"
        return 0
    else
        echo -e "\e[31m[ERROR] FastAPI MySQL server is not running or not accessible at ${BASE_URL}\e[0m"
        echo -e "\e[33m[INFO] To start the server, run: cd mysql_db && uvicorn main:app --reload\e[0m"
        return 1
    fi
}

# Check API availability
if ! check_api; then
    exit 1
fi

# Fetch all patients data (complete records with symptoms and tests)
echo -e "\e[32m[INFO] Fetching complete patient records from MySQL...\e[0m"
PATIENTS_DATA=$(curl -s "${BASE_URL}/mysql/patients" -H "Content-Type: application/json")
if [ $? -eq 0 ]; then
    echo "✓ Complete patient records fetched successfully"
    echo "$PATIENTS_DATA" > complete_patient_data.json
    
    # Also save raw patient data for ML processing
    echo "$PATIENTS_DATA" > patients_data.json
else
    echo -e "\e[31m[ERROR] Failed to fetch patient data from MySQL\e[0m"
fi

# Note: MySQL API provides complete records in a single endpoint
echo -e "\e[33m[INFO] MySQL API provides complete patient records including:\e[0m"
echo "  - Patient demographics (age, sex, restbps, chol, fbs)"
echo "  - Clinical symptoms (cp, exang, oldpeak, slope)"  
echo "  - Cardiac tests (restecg, thalach, ca, thal, target)"

# Step 2: Fetch Data of the Latest Entry
echo -e "\e[34m[INFO] Extracting latest entry for prediction...\e[0m"

if command -v jq >/dev/null 2>&1; then
    echo -e "\e[32m[INFO] Using jq to process JSON data...\e[0m"
    
    # Get latest entry (last patient record)
    LATEST_ENTRY=$(echo "$PATIENTS_DATA" | jq '.[-1]' 2>/dev/null || echo "{}")
    
    if [ "$LATEST_ENTRY" != "{}" ] && [ "$LATEST_ENTRY" != "null" ]; then
        echo "$LATEST_ENTRY" > latest_entry.json
        echo "✓ Latest entry extracted and saved to latest_entry.json"
        echo "Latest patient record: $LATEST_ENTRY"
        
        # Extract features for ML model (reorder for model input)
        FEATURES=$(echo "$LATEST_ENTRY" | jq '[.[1], .[2], .[6], .[3], .[4], .[5], .[10], .[11], .[7], .[8], .[9], .[12], .[13]]' 2>/dev/null)
        echo "$FEATURES" > latest_features.json
        echo "✓ Features extracted for ML prediction: latest_features.json"
        
        # Also create formatted features for display
        FORMATTED_FEATURES=$(echo "$LATEST_ENTRY" | jq '{
            age: .[1], 
            sex: .[2], 
            cp: .[6], 
            restbps: .[3], 
            chol: .[4], 
            fbs: .[5], 
            restecg: .[10], 
            thalach: .[11], 
            exang: .[7], 
            oldpeak: .[8], 
            slope: .[9], 
            ca: .[12], 
            thal: .[13],
            target: .[14]
        }' 2>/dev/null)
        
        echo "$FORMATTED_FEATURES" > ml_features.json
        echo "✓ Formatted ML features saved to ml_features.json"
    else
        echo -e "\e[33m[WARNING] No data found or invalid JSON response from API\e[0m"
    fi
else
    echo -e "\e[33m[WARNING] jq not found. Install with: sudo apt-get install jq\e[0m"
    echo -e "\e[33m[INFO] Saving raw data for manual processing...\e[0m"
fi

# Step 3: Data Validation and Summary
echo -e "\e[34m[INFO] Validating fetched data...\e[0m"

# Check if we have any data (count records in the array)
if command -v jq >/dev/null 2>&1; then
    RECORD_COUNT=$(echo "$PATIENTS_DATA" | jq 'length' 2>/dev/null || echo "0")
else
    # Fallback method - count by looking for patient_id pattern
    RECORD_COUNT=$(echo "$PATIENTS_DATA" | grep -o '\[' | wc -l 2>/dev/null || echo "0")
fi

echo -e "\e[36m[SUMMARY] MySQL Data Summary:\e[0m"
echo "  - Complete Patient Records: $RECORD_COUNT records"
echo "  - Each record includes: Demographics + Symptoms + Cardiac Tests"

# Step 4: Prepare Data for ML Prediction
echo -e "\e[34m[INFO] Preparing data for ML prediction...\e[0m"

if [ "$RECORD_COUNT" -gt 0 ]; then
    echo -e "\e[32m[SUCCESS] Data fetched successfully from FastAPI MySQL Database!\e[0m"
    echo -e "\e[33m[INFO] Data files created:\e[0m"
    echo "  - complete_patient_data.json (all complete patient records)"
    echo "  - patients_data.json (copy for processing)"
    
    if command -v jq >/dev/null 2>&1; then
        echo "  - latest_complete_record.json (latest complete patient record)"
        echo "  - ml_features.json (extracted features ready for ML model)"
    fi
    
    echo -e "\e[33m[NEXT STEPS] You can now:\e[0m"
    echo "  1. Load your heart disease prediction ML model"
    echo "  2. Use ml_features.json for immediate prediction"
    echo "  3. Process complete_patient_data.json for batch predictions"
    echo "  4. Features available: age, sex, cp, restbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal"
else
    echo -e "\e[31m[ERROR] No data found in the MySQL database. Please ensure:\e[0m"
    echo "  1. MySQL server is running and accessible"
    echo "  2. FastAPI server is properly connected to MySQL"
    echo "  3. Patient data has been loaded into the MySQL tables"
    echo "  4. Tables exist: Patients, ClinicalSymptoms, CardiacTests"
fi

echo -e "\e[36m[INFO] Script completed!\e[0m"