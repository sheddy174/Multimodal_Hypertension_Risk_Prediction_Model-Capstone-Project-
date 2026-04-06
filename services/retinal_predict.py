import torch
import torchvision.transforms as transforms
from PIL import Image

from model_architectures.fundus_model import FundusHypertensionModel

model = FundusHypertensionModel()
checkpoint = torch.load("models/best_fundus_htr_model.pth", map_location="cpu", weights_only=False)
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor()
])

def retinal_predict(image: Image):

    img = transform(image).unsqueeze(0)

    with torch.no_grad():
        output = model(img)

    prob = torch.sigmoid(output).item()

    return prob