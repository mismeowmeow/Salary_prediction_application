from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from .database import engine, get_db
from .models import Base, User, Prediction
from .schemas import (
    UserCreate,
    UserResponse,
    Token,
    PredictionInput,
    PredictionResponse,
)
from .auth import (
    hash_password,
    authenticate_user,
    create_access_token,
    get_current_user,
)
from .config import ACCESS_TOKEN_EXPIRE_MINUTES
from .utils import load_model, prepare_features


# Create database tables
Base.metadata.create_all(bind=engine)

# FastAPI app

app = FastAPI(
    title="Salary Prediction API",
    description=(
        "An API for predicting salaries based on test scores, "
        "interview scores, and years of experience"
    ),
    version="1.0.0",
)

# Load ML model

try:
    model = load_model()
except Exception:
    model = None


@app.get("/")
def read_root():
    """API information endpoint"""
    return {
        "message": "Salary Prediction API",
        "version": "1.0.0",
        "description": (
            "An API for predicting salaries based on test scores, "
            "interview scores, and years of experience"
        ),
    }

@app.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""

    # Check if username already exists
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email already exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login using username and password"""

    user = authenticate_user(
        db,
        form_data.username,
        form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@app.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_201_CREATED,
)
def predict_salary(
    input_data: PredictionInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Make a salary prediction (authentication required)"""

    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded",
        )

    try:
        features = prepare_features(
            input_data.test_score,
            input_data.interview_score,
            input_data.years_experience,
        )

        predicted_salary = float(model.predict(features)[0])

        new_prediction = Prediction(
            user_id=current_user.id,
            test_score=input_data.test_score,
            interview_score=input_data.interview_score,
            years_experience=input_data.years_experience,
            predicted_salary=predicted_salary,
        )

        db.add(new_prediction)
        db.commit()
        db.refresh(new_prediction)

        return new_prediction

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction error: {str(e)}",
        )

@app.get(
    "/predictions",
    response_model=List[PredictionResponse],
)
def get_predictions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all predictions for the current user"""

    return (
        db.query(Prediction)
        .filter(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc())
        .all()
    )


@app.get(
    "/predictions/{prediction_id}",
    response_model=PredictionResponse,
)
def get_prediction(
    prediction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific prediction by ID"""

    prediction = (
        db.query(Prediction)
        .filter(
            Prediction.id == prediction_id,
            Prediction.user_id == current_user.id,
        )
        .first()
    )

    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )

    return prediction


@app.get("/me", response_model=UserResponse)
def user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current logged-in user information"""
    return current_user
