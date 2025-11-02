-- Heart Disease Prediction Database Schema
-- MySQL Database Setup with Stored Procedures and Triggers

CREATE DATABASE IF NOT EXISTS heart_disease_db;
USE heart_disease_db;

-- ====================================
-- TABLE DEFINITIONS (3NF Normalized)
-- ====================================

-- 1. Patients table (Demographics)
CREATE TABLE IF NOT EXISTS Patients (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    age INT NOT NULL CHECK (age BETWEEN 1 AND 120),
    sex INT NOT NULL CHECK (sex IN (0, 1)), -- 0: Female, 1: Male
    restbps INT NOT NULL CHECK (restbps BETWEEN 80 AND 200), -- Resting blood pressure
    chol INT NOT NULL CHECK (chol BETWEEN 100 AND 600), -- Serum cholesterol
    fbs INT NOT NULL CHECK (fbs IN (0, 1)), -- Fasting blood sugar > 120 mg/dl
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_age (age),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB;

-- 2. Clinical Symptoms table
CREATE TABLE IF NOT EXISTS ClinicalSymptoms (
    symptom_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    cp INT NOT NULL CHECK (cp BETWEEN 0 AND 3), -- Chest pain type
    exang INT NOT NULL CHECK (exang IN (0, 1)), -- Exercise induced angina
    oldpeak DECIMAL(3,1) NOT NULL CHECK (oldpeak >= 0), -- ST depression
    slope INT NOT NULL CHECK (slope BETWEEN 0 AND 2), -- ST slope
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient_symptoms (patient_id),
    INDEX idx_chest_pain (cp)
) ENGINE=InnoDB;

-- 3. Cardiac Tests table
CREATE TABLE IF NOT EXISTS CardiacTests (
    test_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    restecg INT NOT NULL CHECK (restecg BETWEEN 0 AND 2), -- Resting ECG results
    thalach INT NOT NULL CHECK (thalach BETWEEN 60 AND 220), -- Maximum heart rate
    ca INT NOT NULL CHECK (ca BETWEEN 0 AND 3), -- Number of major vessels
    thal INT NOT NULL CHECK (thal BETWEEN 1 AND 3), -- Thalassemia
    target INT NOT NULL CHECK (target IN (0, 1)), -- Heart disease diagnosis
    test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient_tests (patient_id),
    INDEX idx_target (target)
) ENGINE=InnoDB;

-- 4. Predictions table (for ML results)
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    prediction_result INT NOT NULL CHECK (prediction_result IN (0, 1)),
    probability_no_disease DECIMAL(5,4) NOT NULL,
    probability_disease DECIMAL(5,4) NOT NULL,
    confidence_score DECIMAL(5,4) NOT NULL,
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_version VARCHAR(50) DEFAULT 'v1.0',
    FOREIGN KEY (patient_id) REFERENCES Patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient_predictions (patient_id),
    INDEX idx_prediction_date (predicted_at)
) ENGINE=InnoDB;

-- 5. Audit Log table (for triggers)
CREATE TABLE IF NOT EXISTS patient_audit_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT,
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    old_values JSON,
    new_values JSON,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(100) DEFAULT 'API_USER',
    INDEX idx_patient_audit (patient_id),
    INDEX idx_audit_date (changed_at)
) ENGINE=InnoDB;

-- ====================================
-- STORED PROCEDURES
-- ====================================

-- 1. Get complete patient record with all related data
DELIMITER //
CREATE PROCEDURE GetCompletePatientRecord(IN p_patient_id INT)
BEGIN
    SELECT 
        p.patient_id,
        p.age,
        p.sex,
        p.restbps,
        p.chol,
        p.fbs,
        cs.cp,
        cs.exang,
        cs.oldpeak,
        cs.slope,
        ct.restecg,
        ct.thalach,
        ct.ca,
        ct.thal,
        ct.target,
        p.created_at,
        ct.test_date
    FROM Patients p
    LEFT JOIN ClinicalSymptoms cs ON p.patient_id = cs.patient_id
    LEFT JOIN CardiacTests ct ON p.patient_id = ct.patient_id
    WHERE p.patient_id = p_patient_id;
END //
DELIMITER ;

-- 2. Get latest patient for ML prediction
DELIMITER //
CREATE PROCEDURE GetLatestPatientForPrediction()
BEGIN
    SELECT 
        p.patient_id,
        p.age,
        p.sex,
        p.restbps,
        p.chol,
        p.fbs,
        cs.cp,
        cs.exang,
        cs.oldpeak,
        cs.slope,
        ct.restecg,
        ct.thalach,
        ct.ca,
        ct.thal,
        ct.target
    FROM Patients p
    LEFT JOIN ClinicalSymptoms cs ON p.patient_id = cs.patient_id
    LEFT JOIN CardiacTests ct ON p.patient_id = ct.patient_id
    ORDER BY p.created_at DESC
    LIMIT 1;
END //
DELIMITER ;

-- 3. Get patient statistics
DELIMITER //
CREATE PROCEDURE GetPatientStatistics()
BEGIN
    SELECT 
        COUNT(*) as total_patients,
        AVG(age) as avg_age,
        COUNT(CASE WHEN sex = 1 THEN 1 END) as male_count,
        COUNT(CASE WHEN sex = 0 THEN 1 END) as female_count,
        AVG(chol) as avg_cholesterol,
        AVG(restbps) as avg_blood_pressure
    FROM Patients;
    
    SELECT 
        COUNT(*) as total_predictions,
        AVG(confidence_score) as avg_confidence,
        COUNT(CASE WHEN prediction_result = 1 THEN 1 END) as disease_predictions,
        COUNT(CASE WHEN prediction_result = 0 THEN 1 END) as no_disease_predictions
    FROM predictions;
END //
DELIMITER ;

-- 4. Validate patient data before insertion
DELIMITER //
CREATE PROCEDURE ValidateAndInsertPatient(
    IN p_age INT,
    IN p_sex INT,
    IN p_restbps INT,
    IN p_chol INT,
    IN p_fbs INT,
    OUT p_patient_id INT,
    OUT p_status VARCHAR(100)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_status = 'ERROR: Invalid data or constraint violation';
        SET p_patient_id = 0;
    END;
    
    START TRANSACTION;
    
    -- Validate input data
    IF p_age < 1 OR p_age > 120 THEN
        SET p_status = 'ERROR: Age must be between 1 and 120';
        SET p_patient_id = 0;
        ROLLBACK;
    ELSEIF p_sex NOT IN (0, 1) THEN
        SET p_status = 'ERROR: Sex must be 0 (Female) or 1 (Male)';
        SET p_patient_id = 0;
        ROLLBACK;
    ELSEIF p_restbps < 80 OR p_restbps > 200 THEN
        SET p_status = 'ERROR: Resting blood pressure must be between 80 and 200';
        SET p_patient_id = 0;
        ROLLBACK;
    ELSE
        -- Insert patient
        INSERT INTO Patients (age, sex, restbps, chol, fbs)
        VALUES (p_age, p_sex, p_restbps, p_chol, p_fbs);
        
        SET p_patient_id = LAST_INSERT_ID();
        SET p_status = 'SUCCESS: Patient created successfully';
        COMMIT;
    END IF;
END //
DELIMITER ;

-- ====================================
-- TRIGGERS
-- ====================================

-- 1. Trigger to log patient insertions
DELIMITER //
CREATE TRIGGER log_patient_insert
AFTER INSERT ON Patients
FOR EACH ROW
BEGIN
    INSERT INTO patient_audit_log (patient_id, action, table_name, new_values)
    VALUES (
        NEW.patient_id,
        'INSERT',
        'Patients',
        JSON_OBJECT(
            'patient_id', NEW.patient_id,
            'age', NEW.age,
            'sex', NEW.sex,
            'restbps', NEW.restbps,
            'chol', NEW.chol,
            'fbs', NEW.fbs
        )
    );
END //
DELIMITER ;

-- 2. Trigger to log patient updates
DELIMITER //
CREATE TRIGGER log_patient_update
AFTER UPDATE ON Patients
FOR EACH ROW
BEGIN
    INSERT INTO patient_audit_log (patient_id, action, table_name, old_values, new_values)
    VALUES (
        NEW.patient_id,
        'UPDATE',
        'Patients',
        JSON_OBJECT(
            'age', OLD.age,
            'sex', OLD.sex,
            'restbps', OLD.restbps,
            'chol', OLD.chol,
            'fbs', OLD.fbs
        ),
        JSON_OBJECT(
            'age', NEW.age,
            'sex', NEW.sex,
            'restbps', NEW.restbps,
            'chol', NEW.chol,
            'fbs', NEW.fbs
        )
    );
END //
DELIMITER ;

-- 3. Trigger to log patient deletions
DELIMITER //
CREATE TRIGGER log_patient_delete
BEFORE DELETE ON Patients
FOR EACH ROW
BEGIN
    INSERT INTO patient_audit_log (patient_id, action, table_name, old_values)
    VALUES (
        OLD.patient_id,
        'DELETE',
        'Patients',
        JSON_OBJECT(
            'patient_id', OLD.patient_id,
            'age', OLD.age,
            'sex', OLD.sex,
            'restbps', OLD.restbps,
            'chol', OLD.chol,
            'fbs', OLD.fbs
        )
    );
END //
DELIMITER ;

-- 4. Trigger to validate heart rate ranges
DELIMITER //
CREATE TRIGGER validate_cardiac_tests
BEFORE INSERT ON CardiacTests
FOR EACH ROW
BEGIN
    IF NEW.thalach < 60 OR NEW.thalach > 220 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Invalid heart rate: must be between 60 and 220 bpm';
    END IF;
    
    IF NEW.oldpeak < 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Invalid oldpeak value: cannot be negative';
    END IF;
END //
DELIMITER ;

-- ====================================
-- SAMPLE DATA INSERTION
-- ====================================

-- Insert sample patients for testing
INSERT IGNORE INTO Patients (patient_id, age, sex, restbps, chol, fbs) VALUES
(1, 63, 1, 145, 233, 1),
(2, 37, 1, 130, 250, 0),
(3, 41, 0, 130, 204, 0),
(4, 56, 1, 120, 236, 0),
(5, 57, 0, 120, 354, 0);

-- Insert corresponding symptoms
INSERT IGNORE INTO ClinicalSymptoms (patient_id, cp, exang, oldpeak, slope) VALUES
(1, 3, 0, 2.3, 0),
(2, 2, 0, 3.5, 0),
(3, 1, 0, 1.4, 2),
(4, 1, 0, 0.8, 2),
(5, 0, 1, 0.6, 2);

-- Insert corresponding tests
INSERT IGNORE INTO CardiacTests (patient_id, restecg, thalach, ca, thal, target) VALUES
(1, 0, 150, 0, 1, 1),
(2, 1, 187, 0, 2, 1),
(3, 0, 172, 0, 2, 0),
(4, 1, 178, 0, 2, 0),
(5, 1, 163, 0, 2, 1);

-- ====================================
-- USEFUL QUERIES FOR TESTING
-- ====================================

-- Test stored procedure: Get complete patient record
-- CALL GetCompletePatientRecord(1);

-- Test stored procedure: Get latest patient
-- CALL GetLatestPatientForPrediction();

-- Test stored procedure: Get statistics
-- CALL GetPatientStatistics();

-- View audit log
-- SELECT * FROM patient_audit_log ORDER BY changed_at DESC LIMIT 10;

-- View all patients with complete data
-- SELECT * FROM Patients p 
-- JOIN ClinicalSymptoms cs ON p.patient_id = cs.patient_id 
-- JOIN CardiacTests ct ON p.patient_id = ct.patient_id;

SHOW TABLES;
SHOW TRIGGERS;
SHOW PROCEDURE STATUS WHERE Db = 'heart_disease_db';
