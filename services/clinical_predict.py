import pandas as pd
import joblib
import numpy as np
import time

# Load the trained model and preprocessing pipeline
print("Loading clinical model and pipeline...")
model = joblib.load("models/best_hypertension_model.pkl")
pipeline = joblib.load("models/framingham_preprocessing_pipeline.pkl")
print("✓ Clinical models loaded")

def clinical_predict(data):
    """
    Predict hypertension risk from clinical data.
    Uses the Framingham preprocessing pipeline and trained model.
    
    Args:
        data: dict with clinical features from the frontend
    
    Returns:
        float: probability of hypertension (0-1)
    """
    
    start_time = time.time()
    
    print(f"\nReceived clinical data: {data}")
    
    # Create DataFrame with ALL features the Framingham model expects
    # The pipeline expects these exact column names
    clinical_df = pd.DataFrame({
        'age': [data.get('age', 50)],
        'sex': [data.get('sex', 0)],  # 0=Female, 1=Male
        'cigsPerDay': [data.get('cigsPerDay', 0)],
        'totChol': [data.get('totChol', 200)],  # Total cholesterol
        'sysBP': [data.get('systolic_bp', 120)],  # Frontend sends 'systolic_bp'
        'diaBP': [data.get('diastolic_bp', 80)],  # Frontend sends 'diastolic_bp'
        'BMI': [data.get('bmi', 25)],  # Frontend sends 'bmi'
        'heartRate': [data.get('heartRate', 75)],
        'glucose': [data.get('glucose', 100)],
        'currentSmoker': [data.get('currentSmoker', 0)],  # 0=No, 1=Yes
        'BPMeds': [data.get('BPMeds', 0)],  # BP medications
        'diabetes': [data.get('diabetes', 0)]  # 0=No, 1=Yes
    })
    
    print(f"Clinical DataFrame shape: {clinical_df.shape}")
    print(f"Clinical DataFrame columns: {clinical_df.columns.tolist()}")
    
    try:
        # Apply the preprocessing pipeline
        # This handles scaling, encoding, and any other transformations
        pipeline_start = time.time()
        clinical_processed = pipeline.transform(clinical_df)
        pipeline_time = time.time() - pipeline_start
        print(f"  ├─ Pipeline preprocessing: {pipeline_time:.4f}s")
        print(f"Processed features shape: {clinical_processed.shape}")
        
        # Get prediction probability
        predict_start = time.time()
        prediction = model.predict_proba(clinical_processed)
        predict_time = time.time() - predict_start
        print(f"  ├─ Model prediction: {predict_time:.4f}s")
        
        prob = prediction[0, 1]  # Probability of hypertension
        
        total_time = time.time() - start_time
        print(f"  └─ Total clinical prediction: {total_time:.4f}s")
        
        return prob
        
    except Exception as e:
        print(f"Error during prediction: {e}")
        print(f"Clinical DataFrame that caused error:\n{clinical_df}")
        raise