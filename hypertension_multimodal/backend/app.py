from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import pandas as pd
import joblib
import torch
from PIL import Image
import io

from services.clinical_predict import clinical_predict
from services.retinal_predict import retinal_predict
from services.fusion_predict import fusion_predict

app = FastAPI(title="Hypertension Multimodal AI API")

# allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Hypertension AI API running"}

@app.post("/predict")
async def predict(
    age: float,
    bmi: float,
    systolic_bp: float,
    diastolic_bp: float,
    glucose: float,
    fundus_image: UploadFile = File(...)
):

    # read image
    contents = await fundus_image.read()
    image = Image.open(io.BytesIO(contents))

    # clinical prediction
    clinical_prob = clinical_predict({
        "age": age,
        "bmi": bmi,
        "systolic_bp": systolic_bp,
        "diastolic_bp": diastolic_bp,
        "glucose": glucose
    })

    # retinal prediction
    retinal_prob = retinal_predict(image)

    # fusion
    fused_prob, risk = fusion_predict(clinical_prob, retinal_prob)

    return {
        "clinical_probability": float(clinical_prob),
        "retinal_probability": float(retinal_prob),
        "fused_probability": float(fused_prob),
        "risk_level": risk
    }