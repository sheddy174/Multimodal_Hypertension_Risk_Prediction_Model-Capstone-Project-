import torch
import torchvision.transforms as transforms
from PIL import Image
import os
import time

from model_architectures.fundus_model import FundusHypertensionModel
from services.model_downloader import download_model_from_github

# Detect device (GPU if available, else CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🖥️ Using device: {device.upper()}")
if torch.cuda.is_available():
    print(f"   GPU: {torch.cuda.get_device_name(0)}")

# Download model if not exists
model_path = download_model_from_github()

# Load model with optimization
print("Loading retinal model...")
model = FundusHypertensionModel()
checkpoint = torch.load(model_path, map_location=device, weights_only=False)
model.load_state_dict(checkpoint["model_state_dict"])
model.to(device)
model.eval()

# Optional: Enable mixed precision for faster inference on GPU
if device == "cuda":
    torch.cuda.set_float32_matmul_precision('high')

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                          std=[0.229, 0.224, 0.225])  # ImageNet normalization
])

def retinal_predict(image: Image):
    """Predict hypertension risk from retinal fundus image"""
    try:
        # Preprocess image
        start_preprocess = time.time()
        img = transform(image).unsqueeze(0).to(device)
        preprocess_time = time.time() - start_preprocess
        print(f"  ├─ Image preprocessing: {preprocess_time:.3f}s")

        # Inference
        with torch.no_grad():
            inference_start = time.time()
            # Use amp (Automatic Mixed Precision) for faster inference on GPU
            if device == "cuda":
                with torch.cuda.amp.autocast():
                    output = model(img)
            else:
                output = model(img)
            inference_time = time.time() - inference_start
            print(f"  ├─ Model inference: {inference_time:.3f}s")

        prob = torch.sigmoid(output).item()
        
        total_time = preprocess_time + inference_time
        print(f"  └─ Total retinal prediction: {total_time:.3f}s")

        return prob
    
    except Exception as e:
        print(f"❌ Retinal prediction error: {e}")
        raise