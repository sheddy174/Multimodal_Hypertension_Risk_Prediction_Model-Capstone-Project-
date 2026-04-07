from fastapi import FastAPI, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import numpy as np
import pandas as pd
import joblib
import torch
from PIL import Image
import io
import traceback
import os

from services.clinical_predict import clinical_predict
from services.retinal_predict import retinal_predict
from services.fusion_predict import fusion_predict
from services.risk_breakdown import calculate_risk_breakdown

app = FastAPI(title="Hypertension Multimodal AI API")

class ClinicalData(BaseModel):
    age: float = Field(50.0)
    sex: int = Field(0)
    bmi: float = Field(25.0)
    systolic_bp: float = Field(120.0)
    diastolic_bp: float = Field(80.0)
    glucose: float = Field(100.0)
    totChol: float = Field(200.0)
    heartRate: int = Field(75)
    currentSmoker: int = Field(0)
    cigsPerDay: int = Field(0)
    diabetes: int = Field(0)
    BPMeds: int = Field(0)

class BreakdownRequest(BaseModel):
    clinical_data: dict
    clinical_probability: float
    retinal_probability: float
    fusion_probability: float


def clamp_value(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(min(value, maximum), minimum)


def normalize_value(value: float, baseline: float, span: float) -> float:
    return clamp_value((value - baseline) / span)


def build_risk_breakdown(clinical_data: ClinicalData, retinal_probability: float, fusion_probability: float):
    return [
        {
            "title": "Systolic Blood Pressure",
            "score": normalize_value(clinical_data.systolic_bp, 110, 80),
            "detail": f"Higher systolic pressure is a strong hypertension driver. Current reading: {clinical_data.systolic_bp} mmHg."
        },
        {
            "title": "Diastolic Blood Pressure",
            "score": normalize_value(clinical_data.diastolic_bp, 70, 80),
            "detail": f"Diastolic pressure influences long-term vascular risk. Current reading: {clinical_data.diastolic_bp} mmHg."
        },
        {
            "title": "Age",
            "score": normalize_value(clinical_data.age, 35, 45),
            "detail": f"Hypertension risk generally increases with age. Current age: {clinical_data.age}."
        },
        {
            "title": "BMI",
            "score": normalize_value(clinical_data.bmi, 22, 18),
            "detail": f"Higher BMI is associated with greater cardiovascular strain. Current BMI: {clinical_data.bmi}."
        },
        {
            "title": "Glucose",
            "score": normalize_value(clinical_data.glucose, 90, 120),
            "detail": f"Elevated glucose can contribute to metabolic risk. Current level: {clinical_data.glucose} mg/dL."
        },
        {
            "title": "Cholesterol",
            "score": normalize_value(clinical_data.totChol, 180, 120),
            "detail": f"High cholesterol can worsen vascular health. Current level: {clinical_data.totChol} mg/dL."
        },
        {
            "title": "Smoking Status",
            "score": 1.0 if clinical_data.currentSmoker == 1 else 0.05,
            "detail": "Smoking increases cardiovascular strain." if clinical_data.currentSmoker == 1 else "Non-smoker status lowers risk."
        },
        {
            "title": "Diabetes",
            "score": 1.0 if clinical_data.diabetes == 1 else 0.05,
            "detail": "Diabetes raises hypertension risk." if clinical_data.diabetes == 1 else "No diabetes lowers risk."
        },
        {
            "title": "Blood Pressure Medication",
            "score": 0.95 if clinical_data.BPMeds == 1 else 0.25,
            "detail": "Medication indicates existing hypertension treatment." if clinical_data.BPMeds == 1 else "No BP medications suggests lower treatment dependency."
        },
        {
            "title": "Heart Rate",
            "score": normalize_value(clinical_data.heartRate, 60, 60),
            "detail": f"Higher resting heart rate is often linked with elevated risk. Current rate: {clinical_data.heartRate} bpm."
        },
        {
            "title": "Retinal Model Contribution",
            "score": clamp_value(retinal_probability),
            "detail": "The fundus image model indicates how strongly retinal changes support hypertension risk."
        },
        {
            "title": "Fusion Impact",
            "score": clamp_value(fusion_probability),
            "detail": "The final prediction combines both clinical and retinal evidence."
        }
    ]


@app.post("/breakdown")
def breakdown(payload: BreakdownRequest):
    try:
        breakdown_result = calculate_risk_breakdown(
            payload.clinical_data,
            payload.clinical_probability,
            payload.retinal_probability,
            payload.fusion_probability
        )
        return breakdown_result

    except Exception as e:
        print("Error generating breakdown:", e)
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "error_type": type(e).__name__,
            }
        )

# CORS Configuration
# TODO: Before production, change allow_origins to your specific frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ DEVELOPMENT ONLY - Change for production!"http://127.0.0.1:5500/frontend/index.html
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Hypertension AI API running", "status": "healthy"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Hypertension Multimodal AI API"}

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
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
