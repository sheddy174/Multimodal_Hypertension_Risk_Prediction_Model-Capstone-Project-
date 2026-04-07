# Download Model from GitHub Releases
import requests
import os
import zipfile
import time

def download_model_from_github():
    """Download and extract model from GitHub Releases"""
    zip_url = "https://github.com/sheddy174/Multimodal_Hypertension_Risk_Prediction_Model-Capstone-Project-/releases/download/v1.0/best_fundus_htr_model.zip"
    zip_path = "models/best_fundus_htr_model.zip"
    model_path = "models/best_fundus_htr_model.pth"

    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)

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
            print(f"❌ Download timeout (>60s). Network too slow. Falling back to local model if available.")
            if os.path.exists(model_path):
                print(f"⚠️  Using local model cache: {model_path}")
                return model_path
            else:
                raise RuntimeError("Model download timed out and no local cache available. Please check: 1) Internet connection 2) GitHub release asset exists 3) File size is not too large")
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error downloading model: {e}")
            if os.path.exists(model_path):
                print(f"⚠️  Using local model cache: {model_path}")
                return model_path
            else:
                raise
        
        except zipfile.BadZipFile as e:
            print(f"❌ ZIP extraction error: {e}")
            if os.path.exists(zip_path):
                os.remove(zip_path)
            raise RuntimeError(f"Failed to extract model ZIP: {e}. Try downloading manually from {zip_url}")
        
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise
    
    else:
        model_size = os.path.getsize(model_path)
        print(f"✅ Model found locally: {model_path} ({model_size:,} bytes)")
    
    return model_path