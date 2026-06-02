from pathlib import Path
import torch
from torch import nn
from torch.nn.modules.activation import LeakyReLU
from torch.nn.modules import BatchNorm1d
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "model" / "incident_tracking_system.pth"
VECTORIZER_PATH = BASE_DIR / "model" / "TfidfVectorizer.joblib"
LABEL_ENCODER_PATH = BASE_DIR / "model" / "label_encoder.joblib"


class IncidentTrackingSystem(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer_stack = nn.Sequential(
            nn.Linear(10204, 2048),
            nn.BatchNorm1d(2048),
            nn.LeakyReLU(negative_slope=0.01),
            nn.Dropout(0.5),
            # Hidden Layer 1
            nn.Linear(2048, 512),
            nn.BatchNorm1d(512),
            nn.LeakyReLU(negative_slope=0.01),
            nn.Dropout(0.5),
            # Hidden Layer 2
            nn.Linear(512, 128),
            nn.BatchNorm1d(128),
            nn.LeakyReLU(negative_slope=0.01),
            nn.Dropout(0.5), 
            # Output Layer (10 classes)
            nn.Linear(128, 10),
        )

    def forward(self, x):
        return self.layer_stack(x)


model = IncidentTrackingSystem()
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device("cpu")))

vectorizer = joblib.load(VECTORIZER_PATH)
label_encoder = joblib.load(LABEL_ENCODER_PATH)
