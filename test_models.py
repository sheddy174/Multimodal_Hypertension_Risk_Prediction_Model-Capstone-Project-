from utils.clinical_predict import predict_clinical

# Dummy test input (must match your training feature names exactly)
clinical_input = {
    "age": 45,
    "sysBP": 140,
    "diaBP": 90,
    "cholesterol": 220,
    "BMI": 28,
}

prob = predict_clinical(clinical_input)

print("Clinical Probability:", prob)