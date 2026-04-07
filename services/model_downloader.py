# Download Model from GitHub Releases
import requests
import os

def download_model_from_github():
    """Download model from GitHub Releases"""
    model_url = "https://github.com/sheddy174/Multimodal_Hypertension_Risk_Prediction_Model-Capstone-Project-/releases/download/v1.0/best_fundus_htr_model.pth"
    model_path = "models/best_fundus_htr_model.pth"

    if not os.path.exists(model_path):
        print("Downloading model from GitHub Releases...")
        response = requests.get(model_url)
        response.raise_for_status()

        os.makedirs("models", exist_ok=True)
        with open(model_path, "wb") as f:
            f.write(response.content)
        print("Model downloaded successfully!")

    return model_path