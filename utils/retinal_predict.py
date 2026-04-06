import torch
import numpy as np
import cv2
from PIL import Image
from torchvision import transforms

from model_architectures.fundus_model import FundusHypertensionModel

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model
model = FundusHypertensionModel(backbone='resnet50', pretrained=False)

# checkpoint = torch.load("models/best_fundus_htr_model.pth",
#                         map_location=device)

# model.load_state_dict(checkpoint['model_state_dict'])
# model.to(device)
# model.eval()


checkpoint = torch.load(
    "models/best_fundus_htr_model.pth",
    map_location=device,
    weights_only=False
)

model.load_state_dict(checkpoint['model_state_dict'])
model.to(device)
model.eval()



# CLAHE function
def apply_clahe(img):
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_clahe = clahe.apply(l)
    lab_clahe = cv2.merge([l_clahe, a, b])
    img_clahe = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2RGB)
    return img_clahe


# Transform (must match training)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def predict_retinal(image_file):
    """
    Independent retinal prediction
    Returns probability of hypertension
    """

    image = Image.open(image_file).convert("RGB")
    image = np.array(image)

    # Apply CLAHE
    image = apply_clahe(image)

    # Extract green channel
    green_channel = image[:, :, 1]
    image = cv2.cvtColor(green_channel, cv2.COLOR_GRAY2RGB)

    image = Image.fromarray(image)
    image = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(image)
        prob = torch.sigmoid(logits.squeeze()).item()

    return float(prob)
