import pickle
import pandas as pd
from sklearn.preprocessing import StandardScaler

# Grade mapping
grade_mapping = {'O': 10, 'E': 9, 'A': 8, 'B': 7, 'C': 6, 'D': 5, 'F': 0}

# Dictionary to store scalers for each semester
scalers = {}

# Loop through all 8 semesters
for semester in range(1, 9):
    # Load dataset for the semester
    df = pd.read_csv(f"student_data_semester_{semester}.csv")

    # Convert 'Grade' column to numerical values
    df['Grade'] = df['Grade'].map(grade_mapping)

    # Drop 'Student_ID' if it exists
    if 'Student_ID' in df.columns:
        df = df.drop(columns=['Student_ID'])

    # Ensure only the required features are included
    feature_columns = [col for col in df.columns if col not in ['Grade', 'Dropout_Risk_%']]
    
    # Debugging: Check column names
    print(f"📊 Semester {semester} Feature Columns: {feature_columns}")

    # Extract features for scaling
    X_train = df[feature_columns].values

    # Initialize and fit the scaler for this semester
    scaler = StandardScaler()
    scaler.fit(X_train)

    # Save the scaler with a unique filename
    with open(f"scaler_sem{semester}.pkl", "wb") as f:
        pickle.dump(scaler, f)

    # Store in dictionary for reference
    scalers[semester] = scaler

    print(f"✅ Scaler for Semester {semester} saved successfully.")

print("🎉 All semester scalers created successfully!")
