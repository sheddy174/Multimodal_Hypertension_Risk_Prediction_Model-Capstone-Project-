# Download Model from GitHub Releases
import requests
import os
import zipfile
import time

def download_model_from_github():
    """Download and extract model from GitHub Releases"""
    default_zip_url = "https://github.com/sheddy174/Multimodal_Hypertension_Risk_Prediction_Model-Capstone-Project-/releases/download/v1.0/best_fundus_htr_model.zip"
    zip_url = os.environ.get("FUNDUS_MODEL_ZIP_URL", default_zip_url)
    model_path = os.environ.get("FUNDUS_MODEL_PATH", "models/best_fundus_htr_model.pth")
    zip_path = os.path.splitext(model_path)[0] + ".zip"

    # Create models directory if it doesn't exist
    os.makedirs(os.path.dirname(model_path), exist_ok=True)

    if not os.path.exists(model_path):
        print(f"⏳ Model not found at {model_path}")
        print(f"📥 Attempting to download from GitHub Releases...")
        print(f"   URL: {zip_url}")
        
        try:
            # Download with timeout (30 seconds)
            download_start = time.time()
            print("   Starting download...")
            response = requests.get(zip_url, timeout=60)  # 60 second timeout
            response.raise_for_status()
            download_time = time.time() - download_start

            # Save the ZIP file
            print(f"✓ Download complete ({download_time:.2f}s), saving ZIP...")
            with open(zip_path, "wb") as f:
                f.write(response.content)
            print(f"✓ Saved: {len(response.content):,} bytes")

            # Extract the model file
            print("⏳ Extracting model file...")
            extract_start = time.time()
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("models")
            extract_time = time.time() - extract_start
            print(f"✓ Extracted successfully ({extract_time:.2f}s)")

            # Clean up ZIP file
            os.remove(zip_path)
            print("✓ Cleaned up temporary ZIP file")
            
            # Verify model exists
            if os.path.exists(model_path):
                model_size = os.path.getsize(model_path)
                print(f"✅ Model ready: {model_path} ({model_size:,} bytes)")
            else:
                raise FileNotFoundError(f"Model file not found after extraction: {model_path}")

        except requests.exceptions.Timeout:
            raise RuntimeError(
                "Model download timed out and no local cache is available. "
                "Please upload the retinal model file to Render or provide a valid FUNDUS_MODEL_ZIP_URL."
            )

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else 'unknown'
            if status == 404:
                raise RuntimeError(
                    f"Model ZIP release asset not found at {zip_url} (404). "
                    "Please verify the GitHub release contains the model ZIP, or upload the model directly to Render."
                )
            raise RuntimeError(f"Failed to download model from {zip_url}: {e}")

        except requests.exceptions.RequestException as e:
            raise RuntimeError(
                f"Network error downloading model from {zip_url}: {e}. "
                "If you have the model file locally, upload it to Render or set FUNDUS_MODEL_PATH."
            )

        except zipfile.BadZipFile as e:
            if os.path.exists(zip_path):
                os.remove(zip_path)
            raise RuntimeError(f"Failed to extract model ZIP: {e}. Ensure the ZIP file is valid.")

        except Exception as e:
            raise RuntimeError(f"Unexpected model download error: {e}")
    
    else:
        model_size = os.path.getsize(model_path)
        print(f"✅ Model found locally: {model_path} ({model_size:,} bytes)")
    
    return model_path