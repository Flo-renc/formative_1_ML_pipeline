from fastapi import APIRouter, HTTPException
from mysql_db.models import CompletePatientRecord, PatientResponse, CompletePatientResponse, PatientBase
from mysql_db.database import get_mysql_connection

router = APIRouter(prefix="/mysql", tags=["MySQL Operations"])

# CREATE - Insert a complete patient record
@router.post("/patients", response_model=dict, status_code=201)
def create_patient(record: CompletePatientRecord):
    """
    Create a new patient with clinical symptoms and cardiac tests
    """
    connection = get_mysql_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor()
        
        # Insert patient
        patient_query = """
            INSERT INTO Patients (age, sex, restbps, chol, fbs)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(patient_query, (
            record.patient.age,
            record.patient.sex,
            record.patient.restbps,
            record.patient.chol,
            record.patient.fbs
        ))
        patient_id = cursor.lastrowid
        
        # Insert clinical symptoms
        symptoms_query = """
            INSERT INTO ClinicalSymptoms (patient_id, cp, exang, oldpeak, slope)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(symptoms_query, (
            patient_id,
            record.symptoms.cp,
            record.symptoms.exang,
            record.symptoms.oldpeak,
            record.symptoms.slope
        ))
        
        # Insert cardiac tests
        tests_query = """
            INSERT INTO CardiacTests (patient_id, restecg, thalach, ca, thal, target)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(tests_query, (
            patient_id,
            record.tests.restecg,
            record.tests.thalach,
            record.tests.ca,
            record.tests.thal,
            record.tests.target
        ))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return {
            "message": "Patient record created successfully",
            "patient_id": patient_id
        }
    
    except Exception as e:
        connection.rollback()
        connection.close()
        raise HTTPException(status_code=400, detail=f"Error creating patient: {str(e)}")


# READ - Get all patients
@router.get("/patients", response_model=list)
def get_all_patients():
    """
    Get all patients with their complete records
    """
    connection = get_mysql_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor()
        query = """
            SELECT 
                p.patient_id, p.age, p.sex, p.restbps, p.chol, p.fbs,
                cs.cp, cs.exang, cs.oldpeak, cs.slope,
                ct.restecg, ct.thalach, ct.ca, ct.thal, ct.target
            FROM Patients p
            LEFT JOIN ClinicalSymptoms cs ON p.patient_id = cs.patient_id
            LEFT JOIN CardiacTests ct ON p.patient_id = ct.patient_id
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return results
    
    except Exception as e:
        connection.close()
        raise HTTPException(status_code=400, detail=f"Error fetching patients: {str(e)}")


# READ - Get a single patient by ID
@router.get("/patients/{patient_id}")
def get_patient_by_id(patient_id: int):
    """
    Get a specific patient by their ID
    """
    connection = get_mysql_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor()
        query = """
            SELECT 
                p.patient_id, p.age, p.sex, p.restbps, p.chol, p.fbs,
                cs.cp, cs.exang, cs.oldpeak, cs.slope,
                ct.restecg, ct.thalach, ct.ca, ct.thal, ct.target
            FROM Patients p
            LEFT JOIN ClinicalSymptoms cs ON p.patient_id = cs.patient_id
            LEFT JOIN CardiacTests ct ON p.patient_id = ct.patient_id
            WHERE p.patient_id = %s
        """
        cursor.execute(query, (patient_id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        connection.close()
        raise HTTPException(status_code=400, detail=f"Error fetching patient: {str(e)}")


# UPDATE - Update patient information
@router.put("/patients/{patient_id}")
def update_patient(patient_id: int, record: CompletePatientRecord):
    """
    Update an existing patient's complete record
    """
    connection = get_mysql_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor()
        
        # Check if patient exists
        cursor.execute("SELECT patient_id FROM Patients WHERE patient_id = %s", (patient_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Update patient
        patient_query = """
            UPDATE Patients 
            SET age = %s, sex = %s, restbps = %s, chol = %s, fbs = %s
            WHERE patient_id = %s
        """
        cursor.execute(patient_query, (
            record.patient.age,
            record.patient.sex,
            record.patient.restbps,
            record.patient.chol,
            record.patient.fbs,
            patient_id
        ))
        
        # Update clinical symptoms
        symptoms_query = """
            UPDATE ClinicalSymptoms 
            SET cp = %s, exang = %s, oldpeak = %s, slope = %s
            WHERE patient_id = %s
        """
        cursor.execute(symptoms_query, (
            record.symptoms.cp,
            record.symptoms.exang,
            record.symptoms.oldpeak,
            record.symptoms.slope,
            patient_id
        ))
        
        # Update cardiac tests
        tests_query = """
            UPDATE CardiacTests 
            SET restecg = %s, thalach = %s, ca = %s, thal = %s, target = %s
            WHERE patient_id = %s
        """
        cursor.execute(tests_query, (
            record.tests.restecg,
            record.tests.thalach,
            record.tests.ca,
            record.tests.thal,
            record.tests.target,
            patient_id
        ))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return {
            "message": "Patient record updated successfully",
            "patient_id": patient_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        connection.rollback()
        connection.close()
        raise HTTPException(status_code=400, detail=f"Error updating patient: {str(e)}")


# DELETE - Delete a patient
@router.delete("/patients/{patient_id}")
def delete_patient(patient_id: int):
    """
    Delete a patient and all associated records
    """
    connection = get_mysql_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor()
        
        # Check if patient exists
        cursor.execute("SELECT patient_id FROM Patients WHERE patient_id = %s", (patient_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Delete patient (CASCADE will delete related records)
        cursor.execute("DELETE FROM Patients WHERE patient_id = %s", (patient_id,))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return {
            "message": "Patient record deleted successfully",
            "patient_id": patient_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        connection.rollback()
        connection.close()
        raise HTTPException(status_code=400, detail=f"Error deleting patient: {str(e)}")

