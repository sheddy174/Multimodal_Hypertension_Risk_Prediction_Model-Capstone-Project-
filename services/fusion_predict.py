import joblib
import numpy as np
import sys
from models.fusion_model import LateFusionHypertensionModel

# Fix for pickle loading: make the class available in __main__
sys.modules['__main__'].LateFusionHypertensionModel = LateFusionHypertensionModel

fusion_model = joblib.load("models/late_fusion_model.pkl")

def fusion_predict(clinical_prob, retinal_prob):

    fused = fusion_model.predict_proba(
        [clinical_prob],
        [retinal_prob]
    )[0]

    risk = fusion_model.get_risk_category(fused)

    return fused, risk