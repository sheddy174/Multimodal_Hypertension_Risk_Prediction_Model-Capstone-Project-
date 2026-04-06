import joblib
import pandas as pd

# Load trained model
clinical_model = joblib.load("models/best_hypertension_model.pkl")

# Load preprocessing pipeline
preprocessing_pipeline = joblib.load(
    "models/framingham_preprocessing_pipeline.pkl"
)


def predict_clinical(input_dict):
    """
    Independent clinical prediction
    Returns probability of hypertension
    """

    input_df = pd.DataFrame([input_dict])

    processed_input = preprocessing_pipeline.transform(input_df)

    prob = clinical_model.predict_proba(processed_input)[0][1]

    return float(prob)