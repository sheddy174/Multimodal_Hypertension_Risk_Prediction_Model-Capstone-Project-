import torch
import torch.nn as nn
from torchvision.models import resnet50, ResNet50_Weights


class FundusHypertensionModel(nn.Module):
    def __init__(self, backbone='resnet50', pretrained=False,
                 feature_dim=512, dropout=0.6):
        super().__init__()

        if backbone == 'resnet50':
            weights = ResNet50_Weights.DEFAULT if pretrained else None
            self.backbone = resnet50(weights=weights)

            in_features = self.backbone.fc.in_features
            self.backbone.fc = nn.Identity()
        else:
            raise ValueError("Only resnet50 supported for deployment")

        self.feature_extractor = nn.Sequential(
            nn.Linear(in_features, feature_dim),
            nn.BatchNorm1d(feature_dim),
            nn.ReLU(),
            nn.Dropout(dropout),

            nn.Linear(feature_dim, feature_dim // 2),
            nn.BatchNorm1d(feature_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout * 0.8)
        )

        self.classifier = nn.Linear(feature_dim // 2, 1)

    def forward(self, x):
        x = self.backbone(x)
        features = self.feature_extractor(x)
        logits = self.classifier(features)
        return logits