import torch
import torchvision.transforms as transforms
from PIL import Image
import os

from model_architectures.fundus_model import FundusHypertensionModel

# Check if model file exists
model_path = "models/best_fundus_htr_model.pth"
if not os.path.exists(model_path):
    print(f"Warning: Model file {model_path} not found. Retinal prediction will not work.")
    model = None
else:
    model = FundusHypertensionModel()
    checkpoint = torch.load(model_path, map_location="cpu", weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor()
])

def retinal_predict(image: Image):
    if model is None:
        raise FileNotFoundError(f"Model file {model_path} not found. Please ensure the model file is uploaded to the deployment environment.")

    img = transform(image).unsqueeze(0)

    with torch.no_grad():
        output = model(img)

    prob = torch.sigmoid(output).item()

    return prob