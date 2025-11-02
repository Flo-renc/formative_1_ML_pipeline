# Heart Disease Prediction Database - Entity Relationship Diagram (ERD)

## Database Schema Overview

This ERD represents a normalized relational database design for a heart disease prediction system following 3NF (Third Normal Form).

```
┌─────────────────────────────────────┐
│                                     │
│         HEART DISEASE DB            │
│      ENTITY RELATIONSHIP            │
│           DIAGRAM                   │
│                                     │
└─────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                                  PATIENTS                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│  PK  patient_id      INT              AUTO_INCREMENT                         │
│      age             INT              NOT NULL (1-120)                       │
│      sex             INT              NOT NULL (0=F, 1=M)                    │
│      restbps         INT              NOT NULL (80-200) [Resting BP]         │
│      chol            INT              NOT NULL (100-600) [Cholesterol]       │
│      fbs             INT              NOT NULL (0,1) [Fasting Blood Sugar]   │
│      created_at      TIMESTAMP        DEFAULT CURRENT_TIMESTAMP              │
│      updated_at      TIMESTAMP        ON UPDATE CURRENT_TIMESTAMP            │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ 1
                                      │
                          ┌───────────┼───────────┐
                          │           │           │
                          │ 1         │ 1         │ 1
                          ▼           ▼           ▼
┌─────────────────────────────────────┐ ┌─────────────────────────────────────┐
│         CLINICALSYMPTOMS            │ │           CARDIACTESTS              │
├─────────────────────────────────────┤ ├─────────────────────────────────────┤
│  PK  symptom_id    INT              │ │  PK  test_id       INT              │
│  FK  patient_id    INT              │ │  FK  patient_id    INT              │
│      cp            INT (0-3)        │ │      restecg       INT (0-2)        │
│      exang         INT (0,1)        │ │      thalach       INT (60-220)     │
│      oldpeak       DECIMAL(3,1)     │ │      ca            INT (0-3)        │
│      slope         INT (0-2)        │ │      thal          INT (1-3)        │
│      created_at    TIMESTAMP        │ │      target        INT (0,1)        │
└─────────────────────────────────────┘ │      test_date     TIMESTAMP        │
                          │             └─────────────────────────────────────┘
                          │                           │
                          │                           │
                          │ 1                         │ 1
                          │                           │
                          │                           │
                          ▼                           ▼
                    ┌─────────────────────────────────────┐
                    │           PREDICTIONS               │
                    ├─────────────────────────────────────┤
                    │  PK  prediction_id      INT         │
                    │  FK  patient_id         INT         │
                    │      prediction_result  INT (0,1)   │
                    │      probability_no_dis DECIMAL(5,4)│
                    │      probability_disease DECIMAL(5,4)│
                    │      confidence_score   DECIMAL(5,4)│
                    │      predicted_at       TIMESTAMP   │
                    │      model_version      VARCHAR(50) │
                    └─────────────────────────────────────┘
                                      │
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │        PATIENT_AUDIT_LOG            │
                    ├─────────────────────────────────────┤
                    │  PK  log_id         INT             │
                    │      patient_id     INT             │
                    │      action         VARCHAR(50)     │
                    │      table_name     VARCHAR(50)     │
                    │      old_values     JSON            │
                    │      new_values     JSON            │
                    │      changed_at     TIMESTAMP       │
                    │      changed_by     VARCHAR(100)    │
                    └─────────────────────────────────────┘
```

## Relationship Details

### 1. PATIENTS (1) ←→ (1) CLINICALSYMPTOMS
- **Relationship**: One-to-One
- **Foreign Key**: ClinicalSymptoms.patient_id → Patients.patient_id
- **Constraint**: CASCADE DELETE
- **Description**: Each patient has exactly one set of clinical symptoms recorded

### 2. PATIENTS (1) ←→ (1) CARDIACTESTS  
- **Relationship**: One-to-One
- **Foreign Key**: CardiacTests.patient_id → Patients.patient_id
- **Constraint**: CASCADE DELETE
- **Description**: Each patient has exactly one set of cardiac test results

### 3. PATIENTS (1) ←→ (M) PREDICTIONS
- **Relationship**: One-to-Many
- **Foreign Key**: predictions.patient_id → Patients.patient_id
- **Constraint**: CASCADE DELETE
- **Description**: Each patient can have multiple ML predictions over time

### 4. PATIENTS (1) ←→ (M) PATIENT_AUDIT_LOG
- **Relationship**: One-to-Many  
- **Foreign Key**: patient_audit_log.patient_id → Patients.patient_id
- **Constraint**: No foreign key constraint (for audit integrity)
- **Description**: Each patient can have multiple audit log entries

## Data Dictionary

### PATIENTS Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| patient_id | INT | PK, AUTO_INCREMENT | Unique patient identifier |
| age | INT | NOT NULL, 1-120 | Patient age in years |
| sex | INT | NOT NULL, 0 or 1 | Gender (0=Female, 1=Male) |
| restbps | INT | NOT NULL, 80-200 | Resting blood pressure (mmHg) |
| chol | INT | NOT NULL, 100-600 | Serum cholesterol (mg/dl) |
| fbs | INT | NOT NULL, 0 or 1 | Fasting blood sugar >120mg/dl (1=true) |

### CLINICALSYMPTOMS Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| symptom_id | INT | PK, AUTO_INCREMENT | Unique symptom record ID |
| patient_id | INT | FK, NOT NULL | Reference to Patients table |
| cp | INT | NOT NULL, 0-3 | Chest pain type (0-3) |
| exang | INT | NOT NULL, 0 or 1 | Exercise induced angina (1=yes) |
| oldpeak | DECIMAL(3,1) | NOT NULL, ≥0 | ST depression induced by exercise |
| slope | INT | NOT NULL, 0-2 | Slope of peak exercise ST segment |

### CARDIACTESTS Table
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| test_id | INT | PK, AUTO_INCREMENT | Unique test record ID |
| patient_id | INT | FK, NOT NULL | Reference to Patients table |
| restecg | INT | NOT NULL, 0-2 | Resting electrocardiographic results |
| thalach | INT | NOT NULL, 60-220 | Maximum heart rate achieved |
| ca | INT | NOT NULL, 0-3 | Number of major vessels colored |
| thal | INT | NOT NULL, 1-3 | Thalassemia (3=normal, 6=fixed, 7=reversible) |
| target | INT | NOT NULL, 0 or 1 | Heart disease presence (1=disease) |

## Normalization Analysis

### First Normal Form (1NF) ✅
- All tables have atomic values
- Each column contains single values
- No repeating groups

### Second Normal Form (2NF) ✅  
- All tables are in 1NF
- All non-key attributes are fully dependent on primary keys
- No partial dependencies exist

### Third Normal Form (3NF) ✅
- All tables are in 2NF
- No transitive dependencies
- All non-key attributes depend directly on primary keys only

## Indexes for Performance

### Primary Indexes
- patient_id (clustered index on all tables)

### Secondary Indexes  
- idx_age ON Patients(age)
- idx_created_at ON Patients(created_at)
- idx_patient_symptoms ON ClinicalSymptoms(patient_id)
- idx_chest_pain ON ClinicalSymptoms(cp)
- idx_patient_tests ON CardiacTests(patient_id)
- idx_target ON CardiacTests(target)
- idx_patient_predictions ON predictions(patient_id)
- idx_prediction_date ON predictions(predicted_at)

## Stored Procedures

1. **GetCompletePatientRecord(patient_id)** - Retrieves complete patient data with JOIN
2. **GetLatestPatientForPrediction()** - Gets most recent patient for ML processing
3. **GetPatientStatistics()** - Returns database statistics
4. **ValidateAndInsertPatient()** - Validates and safely inserts patient data

## Triggers

1. **log_patient_insert** - Logs patient creation to audit table
2. **log_patient_update** - Logs patient modifications to audit table  
3. **log_patient_delete** - Logs patient deletions to audit table
4. **validate_cardiac_tests** - Validates cardiac test data before insertion

## Business Rules

1. Each patient must have complete demographic, symptom, and test data
2. All numeric values must be within medically valid ranges
3. All database changes are logged for audit purposes
4. ML predictions are stored with confidence scores and timestamps
5. Patient data cannot be orphaned (CASCADE DELETE ensures referential integrity)
