from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
import pandas as pd
import joblib
import torch
from PIL import Image
import io
import traceback

from services.clinical_predict import clinical_predict
from services.retinal_predict import retinal_predict
from services.fusion_predict import fusion_predict

app = FastAPI(title="Hypertension Multimodal AI API")

# CORS Configuration
# TODO: Before production, change allow_origins to your specific frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500/frontend/index.html"],  # ⚠️ DEVELOPMENT ONLY - Change for production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Hypertension AI API running"}

@app.post("/predict")
async def predict(
    # Required fields from frontend
    age: float = Form(...),
    bmi: float = Form(...),
    systolic_bp: float = Form(...),
    diastolic_bp: float = Form(...),
    glucose: float = Form(...),
    
    # Optional fields with defaults for missing Framingham features
    sex: int = Form(0),  # Default: 0=Female
    currentSmoker: int = Form(0),  # Default: 0=No
    cigsPerDay: int = Form(0),  # Default: 0 cigarettes
    diabetes: int = Form(0),  # Default: 0=No
    totChol: float = Form(200.0),  # Default: 200 mg/dL (average)
    heartRate: int = Form(75),  # Default: 75 bpm (average)
    BPMeds: int = Form(0),  # Default: 0=No BP medications
    
    # Image upload
    fundus_image: UploadFile = File(...)
):
    """
    Predict hypertension risk using clinical data and retinal fundus image.
    
    The Framingham model requires 12 clinical features.
    Frontend provides 5, we use sensible defaults for the remaining 7.
    """
    
    print("\n" + "="*60)
    print("NEW PREDICTION REQUEST")
    print("="*60)
    print("\n📊 CLINICAL DATA RECEIVED:")
    print(f"  Age: {age}")
    print(f"  Sex: {sex} (0=Female, 1=Male)")
    print(f"  BMI: {bmi}")
    print(f"  Systolic BP: {systolic_bp}")
    print(f"  Diastolic BP: {diastolic_bp}")
    print(f"  Glucose: {glucose}")
    print(f"  Total Cholesterol: {totChol}")
    print(f"  Heart Rate: {heartRate}")
    print(f"  Current Smoker: {currentSmoker}")
    print(f"  Cigarettes/Day: {cigsPerDay}")
    print(f"  Diabetes: {diabetes}")
    print(f"  BP Medications: {BPMeds}")
    print(f"\n🖼️ IMAGE INFO:")
    print(f"  Filename: {fundus_image.filename}")
    print(f"  Content Type: {fundus_image.content_type}")
    
    try:
        # Step 1: Read and process image
        print("\n[STEP 1/4] 📷 Reading fundus image...")
        contents = await fundus_image.read()
        print(f"  ✓ Image size: {len(contents):,} bytes")
        
        image = Image.open(io.BytesIO(contents))
        print(f"  ✓ Image loaded: {image.format}, {image.size}, {image.mode}")

        # Step 2: Clinical prediction using Framingham model + pipeline
        print("\n[STEP 2/4] 🔬 Running clinical prediction...")
        print("  Using Framingham preprocessing pipeline...")
        
        clinical_data = {
            "age": age,
            "sex": sex,
            "bmi": bmi,
            "systolic_bp": systolic_bp,  # Will be mapped to sysBP
            "diastolic_bp": diastolic_bp,  # Will be mapped to diaBP
            "glucose": glucose,
            "totChol": totChol,
            "heartRate": heartRate,
            "currentSmoker": currentSmoker,
            "cigsPerDay": cigsPerDay,
            "diabetes": diabetes,
            "BPMeds": BPMeds
        }
        
        clinical_prob = clinical_predict(clinical_data)
        print(f"  ✓ Clinical probability: {clinical_prob:.4f}")

        # Step 3: Retinal prediction using ResNet-50
        print("\n[STEP 3/4] 👁️ Running retinal prediction...")
        retinal_prob = retinal_predict(image)
        print(f"  ✓ Retinal probability: {retinal_prob:.4f}")

        # Step 4: Fusion of both models
        print("\n[STEP 4/4] 🔗 Running late fusion...")
        fused_prob, risk = fusion_predict(clinical_prob, retinal_prob)
        print(f"  ✓ Fused probability: {fused_prob:.4f}")
        print(f"  ✓ Risk level: {risk}")
        
        print("\n" + "="*60)
        print("✅ PREDICTION SUCCESSFUL")
        print("="*60)
        print(f"Clinical: {clinical_prob:.4f} | Retinal: {retinal_prob:.4f} | Fused: {fused_prob:.4f}")
        print(f"Risk: {risk}")
        print("="*60 + "\n")

        return {
            "clinical_probability": float(clinical_prob),
            "retinal_probability": float(retinal_prob),
            "fused_probability": float(fused_prob),
            "risk_level": risk
        }
    
    except Exception as e:
        # Log the full error with stack trace
        print("\n" + "="*60)
        print("❌ ERROR OCCURRED")
        print("="*60)
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print("\n📋 FULL TRACEBACK:")
        print(traceback.format_exc())
        print("="*60 + "\n")
        
        # Return a proper error response
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "error_type": type(e).__name__,
                "clinical_probability": 0.0,
                "retinal_probability": 0.0,
                "fused_probability": 0.0,
                "risk_level": "Error"
            }
        )
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
