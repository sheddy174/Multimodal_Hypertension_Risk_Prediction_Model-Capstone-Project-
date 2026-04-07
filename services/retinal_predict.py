import torch
import torchvision.transforms as transforms
from PIL import Image
import os
import time
import signal

from model_architectures.fundus_model import FundusHypertensionModel
from services.model_downloader import download_model_from_github

# Detect device (GPU if available, else CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🖥️ Using device: {device.upper()}")
if torch.cuda.is_available():
    try:
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
    except Exception as e:
        print(f"   GPU detected but error getting name: {e}")

# Model will be loaded on first use (lazy loading to avoid startup delays)
model = None
model_load_attempted = False

def timeout_handler(signum, frame):
    """Handler for timeout signals"""
    raise TimeoutError("Retinal model inference exceeded timeout")

def load_retinal_model():
    """Lazy load retinal model on first use"""
    global model, model_load_attempted
    
    if model is not None:
        return model
    
    if model_load_attempted:
        raise RuntimeError("Retinal model loading previously failed")
    
    print("⏳ Loading retinal model (first inference)...")
    load_start = time.time()
    
    try:
        model_path = download_model_from_github()
        
        print(f"🔧 Building model architecture...")
        model = FundusHypertensionModel()
        
        print(f"📁 Loading checkpoint from {model_path}...")
        checkpoint = torch.load(model_path, map_location=device, weights_only=False)
        model.load_state_dict(checkpoint["model_state_dict"])
        model.to(device)
        model.eval()
        
        # Optional: Enable mixed precision for faster inference on GPU
        if device == "cuda":
            torch.cuda.set_float32_matmul_precision('high')
        
        load_time = time.time() - load_start
        model_load_attempted = True
        print(f"✅ Retinal model loaded successfully ({load_time:.2f}s)")
        
        return model
    
    except Exception as e:
        print(f"❌ Failed to load retinal model: {e}")
        model_load_attempted = False
        raise

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                          std=[0.229, 0.224, 0.225])  # ImageNet normalization
])

def retinal_predict(image: Image, timeout_seconds=120):
    """
    Predict hypertension risk from retinal fundus image
    
    Args:
        image: PIL Image object
        timeout_seconds: Maximum time allowed for prediction (default 120s)
    
    Returns:
        float: probability between 0 and 1
    """
    global model
    
    try:
        # Set timeout using signal (Unix/Linux/Mac only, for production consider using concurrent.futures)
        if hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)
        
        # Load model if not already loaded
        if model is None:
            model = load_retinal_model()
        
        # Preprocess image
        start_preprocess = time.time()
        img = transform(image).unsqueeze(0).to(device)
        preprocess_time = time.time() - start_preprocess
        print(f"  ├─ Image preprocessing: {preprocess_time:.3f}s")

        # Inference with timeout
        print(f"  ├─ Running inference ({device.upper()})...")
        with torch.no_grad():
            inference_start = time.time()
            # Use amp (Automatic Mixed Precision) for faster inference on GPU
            if device == "cuda":
                try:
                    with torch.cuda.amp.autocast():
                        output = model(img)
                except Exception as e:
                    print(f"  ⚠️  AMP failed, falling back to standard inference: {e}")
                    output = model(img)
            else:
                output = model(img)
            inference_time = time.time() - inference_start
            print(f"  ├─ Model inference: {inference_time:.3f}s")

        prob = torch.sigmoid(output).item()
        
        total_time = preprocess_time + inference_time
        print(f"  └─ Total retinal prediction: {total_time:.3f}s")
        
        # Cancel the alarm if set
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
        
        return prob
    
    except TimeoutError as e:
        print(f"❌ Retinal prediction timeout: {e}")
        # Cancel alarm
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
        raise RuntimeError(f"Retinal model inference took too long (>{timeout_seconds}s). Consider GPU acceleration or model optimization.")
    
    except Exception as e:
        print(f"❌ Retinal prediction error: {e}")
        # Cancel alarm
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)
        raise