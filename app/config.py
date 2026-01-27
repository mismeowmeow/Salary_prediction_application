import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DATABASE_URL = "sqlite:///./salary_predictor.db"

# Security
SECRET_KEY = "your-secret-key-change-this-in-production-make-it-long-and-random"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Model
MODEL_PATH = os.path.join(BASE_DIR, "trained_models", "salary_model.pkl")