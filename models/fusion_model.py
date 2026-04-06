import numpy as np

class LateFusionHypertensionModel:

    def __init__(self, fusion_strategy="weighted", clinical_weight=0.65, image_weight=0.35):
        self.fusion_strategy = fusion_strategy
        self.clinical_weight = clinical_weight
        self.image_weight = image_weight
        self.meta_classifier = None

        # Normalize weights
        total_weight = self.clinical_weight + self.image_weight
        self.clinical_weight /= total_weight
        self.image_weight /= total_weight

    def predict_proba(self, clinical_probs, image_probs):
        """
        Fuse predictions from clinical and image models
        """

        clinical_probs = np.array(clinical_probs).flatten()
        image_probs = np.array(image_probs).flatten()

        if self.fusion_strategy == "average":
            fused_probs = (clinical_probs + image_probs) / 2

        elif self.fusion_strategy == "weighted":
            fused_probs = (
                self.clinical_weight * clinical_probs
                + self.image_weight * image_probs
            )

        else:
            raise ValueError(f"Unknown fusion strategy: {self.fusion_strategy}")

        return fused_probs

    def predict(self, clinical_probs, image_probs, threshold=0.5):
        """
        Convert probability to binary prediction
        """
        fused_probs = self.predict_proba(clinical_probs, image_probs)
        return (fused_probs >= threshold).astype(int)

    def get_risk_category(self, probability):
        """
        Convert probability to risk category
        """

        if probability < 0.4:
            return "Low Risk"

        elif probability < 0.75:
            return "Medium Risk"

        else:
            return "High Risk"