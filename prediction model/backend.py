from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, validator
import numpy as np
import tensorflow as tf
import uvicorn
import pickle
import plotly.express as px
import pandas as pd
import json
import os

# Define subject distribution per semester (Theory, Practical)
SEMESTER_SUBJECTS = {
    1: (3, 3),   # 3 Theory, 3 Practical
    2: (4, 4),   # 4 Theory, 4 Practical
    3: (6, 4),   # 6 Theory, 4 Practical
    4: (7, 3),   # 7 Theory, 3 Practical
    5: (7, 3),   # 7 Theory, 3 Practical
    6: (7, 3),   # 7 Theory, 3 Practical
    7: (6, 0),   # 6 Theory, 0 Practical
    8: (4, 0)    # 4 Theory, 0 Practical
}

# Maximum marks
MAX_CA_MARKS = 25  # Maximum marks for CA
MAX_PCA_MARKS = 40  # Maximum marks for PCA

# Grade Mapping
GRADE_MAPPING = {
    10: "O",  # For very low dropout risk (< 5%)
    9: "E",   # For low dropout risk (5-15%)
    8: "A",   # 70-79%
    7: "B",   # 60-69%
    6: "C",   # 50-59%
    5: "D",   # 40-49%
    4: "F"    # 0-39%
}

# Dropout Risk Adjustment based on Grades
grade_to_dropout_range = {
    10: (0, 5),    # O
    9: (3, 10),    # E
    8: (5, 15),    # A
    7: (10, 25),   # B
    6: (15, 40),   # C
    5: (25, 75),   # D
    0: (50, 99)    # F
}

# Load models for all semesters
models = {}
for i in range(1, 9):
    try:
        models[f"sem{i}"] = {
            "grade": tf.keras.models.load_model(f"grade_prediction_model{i}.h5"),
            "dropout": tf.keras.models.load_model(f"dropout_risk_prediction_model{i}.h5")
        }
        print(f"✅ Successfully loaded models for Semester {i}")
    except Exception as e:
        print(f"❌ Error loading models for Semester {i}: {e}")

# Load scalers for all semesters
scalers = {}
for i in range(1, 9):
    try:
        with open(f"scaler_sem{i}.pkl", "rb") as f:
            scalers[i] = pickle.load(f)
        print(f"✅ Scaler for Semester {i} loaded successfully.")
    except Exception as e:
        print(f"❌ Error loading scaler for Semester {i}: {e}")

app = FastAPI()

# Add CORS middleware with more permissive configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Add static file serving
app.mount("/static", StaticFiles(directory="."), name="static")

# Add dashboard endpoints
@app.get("/")
async def root():
    return FileResponse("dashboard.html")

@app.get("/dashboard/semester/{semester}/summary")
async def get_semester_summary(semester: int):
    try:
        # Load data from Excel file
        df = pd.read_excel("student_data.xlsx")
        semester_data = df[df['Semester'] == semester]
        
        # Calculate summary statistics
        summary = {
            "total_students": len(semester_data),
            "average_grade": semester_data['Grade'].mean(),
            "dropout_risk": semester_data['Dropout_Risk'].mean(),
            "attendance_rate": semester_data['Attendance'].mean(),
            "behavior_score": semester_data['Behavior'].mean()
        }
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/semester/{semester}/grade-distribution")
async def get_grade_distribution(semester: int):
    try:
        df = pd.read_excel("student_data.xlsx")
        semester_data = df[df['Semester'] == semester]
        
        # Create grade distribution plot
        fig = px.histogram(semester_data, x='Grade', 
                          title=f'Grade Distribution - Semester {semester}',
                          labels={'Grade': 'Grade', 'count': 'Number of Students'})
        
        return json.loads(fig.to_json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/semester/{semester}/dropout-risk")
async def get_dropout_risk(semester: int):
    try:
        df = pd.read_excel("student_data.xlsx")
        semester_data = df[df['Semester'] == semester]
        
        # Create dropout risk distribution plot
        fig = px.histogram(semester_data, x='Dropout_Risk',
                          title=f'Dropout Risk Distribution - Semester {semester}',
                          labels={'Dropout_Risk': 'Dropout Risk (%)', 'count': 'Number of Students'})
        
        return json.loads(fig.to_json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/semester/{semester}/attendance-vs-grade")
async def get_attendance_vs_grade(semester: int):
    try:
        df = pd.read_excel("student_data.xlsx")
        semester_data = df[df['Semester'] == semester]
        
        # Create attendance vs grade scatter plot
        fig = px.scatter(semester_data, x='Attendance', y='Grade',
                        title=f'Attendance vs Grade - Semester {semester}',
                        labels={'Attendance': 'Attendance (%)', 'Grade': 'Grade'})
        
        return json.loads(fig.to_json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/semester/{semester}/behavior-vs-grade")
async def get_behavior_vs_grade(semester: int):
    try:
        df = pd.read_excel("student_data.xlsx")
        semester_data = df[df['Semester'] == semester]
        
        # Create behavior vs grade scatter plot
        fig = px.scatter(semester_data, x='Behavior', y='Grade',
                        title=f'Behavior vs Grade - Semester {semester}',
                        labels={'Behavior': 'Behavior Score', 'Grade': 'Grade'})
        
        return json.loads(fig.to_json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/semester/{semester}/marks-analysis")
async def get_marks_analysis(semester: int):
    try:
        df = pd.read_excel("student_data.xlsx")
        semester_data = df[df['Semester'] == semester]
        
        # Calculate CA and PCA statistics
        analysis = {
            "ca_stats": {
                "mean": semester_data['CA_Marks'].mean(),
                "std": semester_data['CA_Marks'].std(),
                "min": semester_data['CA_Marks'].min(),
                "max": semester_data['CA_Marks'].max()
            },
            "pca_stats": {
                "mean": semester_data['PCA_Marks'].mean(),
                "std": semester_data['PCA_Marks'].std(),
                "min": semester_data['PCA_Marks'].min(),
                "max": semester_data['PCA_Marks'].max()
            }
        }
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/semester/{semester}/weakest-subjects")
async def get_weakest_subjects(semester: int):
    try:
        df = pd.read_excel("student_data.xlsx")
        semester_data = df[df['Semester'] == semester]
        
        # Calculate average marks for each subject
        subject_marks = {}
        for col in semester_data.columns:
            if col.startswith('Subject_'):
                subject_marks[col] = semester_data[col].mean()
        
        # Sort subjects by marks and get the weakest ones
        weakest_subjects = dict(sorted(subject_marks.items(), key=lambda x: x[1])[:3])
        
        return weakest_subjects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Define request schema
class PredictionRequest(BaseModel):
    semester: int
    marks: list  # List of marks (CA/PCA for subjects)
    behavior: int
    attendance: int
    subject: int = None  # Optional: If provided, predict for a single subject

    @validator('behavior')
    def validate_behavior(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('Behavior score must be between 1 and 10')
        return v

    @validator('attendance')
    def validate_attendance(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Attendance must be between 0 and 100')
        return v

    @validator('marks')
    def validate_marks(cls, v):
        if not all(isinstance(mark, (int, float)) for mark in v):
            raise ValueError('All marks must be numbers')
        return v

    @validator('semester')
    def validate_semester(cls, v):
        if not 1 <= v <= 8:
            raise ValueError('Semester must be between 1 and 8')
        return v

def validate_marks(semester: int, marks: list, subject: int = None) -> bool:
    num_theory, num_practical = SEMESTER_SUBJECTS[semester]
    
    if subject is not None:
        # Single subject prediction
        if subject <= num_theory:
            # Theory subject (4 CA marks)
            return len(marks) == 4
        elif subject <= num_theory + num_practical:
            # Practical subject (2 PCA marks)
            return len(marks) == 2
        else:
            return False
    else:
        # All subjects prediction
        expected_marks = (num_theory * 4) + (num_practical * 2)
        return len(marks) == expected_marks

def calculate_percentage_marks(marks: list, semester: int) -> float:
    num_theory, num_practical = SEMESTER_SUBJECTS[semester]
    theory_marks = marks[:num_theory * 4]
    practical_marks = marks[num_theory * 4:]
    
    # Calculate theory percentage (4 CA marks per subject, max 25 each)
    theory_total = sum(theory_marks)
    theory_max = num_theory * 4 * MAX_CA_MARKS
    theory_percentage = (theory_total / theory_max) * 100 if theory_max > 0 else 0
    
    # Calculate practical percentage (2 PCA marks per subject, max 40 each)
    practical_total = sum(practical_marks)
    practical_max = num_practical * 2 * MAX_PCA_MARKS
    practical_percentage = (practical_total / practical_max) * 100 if practical_max > 0 else 0
    
    # Weighted average (70% theory, 30% practical)
    return (theory_percentage * 0.7) + (practical_percentage * 0.3)

def get_grade_from_percentage(percentage: float) -> str:
    if percentage >= 90:
        return "O"
    elif percentage >= 80:
        return "E"
    elif percentage >= 70:
        return "A"
    elif percentage >= 60:
        return "B"
    elif percentage >= 50:
        return "C"
    elif percentage >= 40:
        return "D"
    else:
        return "F"

@app.post("/predict")
async def predict(request: PredictionRequest):
    try:
        semester = request.semester
        marks = request.marks
        behavior = request.behavior
        attendance = request.attendance
        subject = request.subject

        # Validate semester
        if semester not in SEMESTER_SUBJECTS:
            raise HTTPException(status_code=400, detail="Invalid semester. Choose between 1 and 8.")

        # Validate marks based on semester and subject
        if not validate_marks(semester, marks, subject):
            num_theory, num_practical = SEMESTER_SUBJECTS[semester]
            if subject is not None:
                expected_marks = 4 if subject <= num_theory else 2
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid number of marks for subject {subject}. Expected {expected_marks} marks."
                )
            else:
                expected_marks = (num_theory * 4) + (num_practical * 2)
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid number of marks. Expected {expected_marks} marks for all subjects."
                )

        # Prepare input data
        # Convert behavior from 1-10 scale to 0-100 scale for the model
        behavior_scaled = (behavior - 1) * (100 / 9)  # Map 1-10 to 0-100
        input_data = np.array(marks + [behavior_scaled, attendance]).reshape(1, -1)

        # Transform input data using the scaler
        input_data_scaled = scalers[semester].transform(input_data)

        # Make predictions using the trained models
        grade_pred = float(models[f"sem{semester}"]["grade"].predict(input_data_scaled)[0][0])
        dropout_pred = float(models[f"sem{semester}"]["dropout"].predict(input_data_scaled)[0][0])

        # Round the grade prediction to nearest integer
        rounded_grade = int(round(grade_pred))
        
        # Adjust grade based on dropout risk
        if dropout_pred < 5:  # Very low dropout risk
            rounded_grade = 10  # O grade
        elif dropout_pred < 15:  # Low dropout risk
            rounded_grade = 9   # E grade
        elif dropout_pred < 25:  # Moderate dropout risk
            rounded_grade = 8   # A grade
        elif dropout_pred < 40:  # High dropout risk
            rounded_grade = 7   # B grade
        elif dropout_pred < 60:  # Very high dropout risk
            rounded_grade = 6   # C grade
        elif dropout_pred < 80:  # Critical dropout risk
            rounded_grade = 5   # D grade
        else:  # Extreme dropout risk
            rounded_grade = 4   # F grade

        # Ensure dropout risk is within valid range (0-100)
        dropout_pred = max(0, min(100, dropout_pred))

        # Convert Numeric Grade to Letter Grade
        letter_grade = GRADE_MAPPING.get(rounded_grade, "F")

        return {
            "semester": semester,
            "subject": f"Subject {subject}" if subject is not None else "All subjects",
            "predicted_grade": letter_grade,
            "predicted_dropout_risk": round(dropout_pred, 2),
            "raw_grade": grade_pred,
            "rounded_grade": rounded_grade
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
