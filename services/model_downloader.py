# Download Model from GitHub Releases
import requests
import os
import zipfile

def download_model_from_github():
    """Download and extract model from GitHub Releases"""
    zip_url = "https://github.com/sheddy174/Multimodal_Hypertension_Risk_Prediction_Model-Capstone-Project-/releases/download/v1.0/best_fundus_htr_model.zip"
    zip_path = "models/best_fundus_htr_model.zip"
    model_path = "models/best_fundus_htr_model.pth"

    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)

    if not os.path.exists(model_path):
        print("Downloading model from GitHub Releases...")
        try:
            # Download the ZIP file
            response = requests.get(zip_url)
            response.raise_for_status()

            # Save the ZIP file
            with open(zip_path, "wb") as f:
                f.write(response.content)
            print(f"Downloaded ZIP file: {len(response.content)} bytes")

            # Extract the model file
            print("Extracting model file...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("models")
            print("Model extracted successfully!")

            # Clean up ZIP file
            os.remove(zip_path)
            print("Cleaned up temporary ZIP file")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading model: {e}")
            raise
        except zipfile.BadZipFile as e:
            print(f"Error extracting ZIP file: {e}")
            raise

    return model_path