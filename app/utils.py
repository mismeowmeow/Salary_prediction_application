import pickle
import os
from .config import MODEL_PATH

def load_model():
    """Load the trained model from pickle file"""
    if not os.path.exists(MODEL_PATH):
        print(f"Warning: Model file not found at {MODEL_PATH}")
        return None
    
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        print(f"Model loaded successfully from {MODEL_PATH}")
        return model
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return None

def prepare_features(test_score: float, interview_score: float, years_experience: float):
    """
    Prepare features for model prediction
    
    Args:
        test_score: Test score (0-100)
        interview_score: Interview score (0-100)
        years_experience: Years of experience
        
    Returns:
        List of features in correct order for model
    """
    # Arrange features in the order your model was trained
    # Adjust if your model expects a different order
    features = [test_score, interview_score, years_experience]
    return [features]  # Return as 2D array for sklearn predict