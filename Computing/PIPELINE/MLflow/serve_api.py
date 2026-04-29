#!/usr/bin/env python3
"""
FastAPI REST API Server for Fish Weight Prediction
This script provides a RESTful API for making fish weight predictions.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
import os
import logging
import mlflow
import mlflow.sklearn
import joblib
from sklearn.preprocessing import LabelEncoder
from typing import List, Optional
import uvicorn
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Fish Weight Prediction API",
    description="REST API for predicting fish weight based on physical measurements using MLflow and scikit-learn",
    version="1.0.0"
)

# Global variables for model and encoder
model = None
label_encoder = None

# Pydantic models for API
class FishInput(BaseModel):
    species: str = Field(..., description="Fish species", example="Bream")
    length1: float = Field(..., description="Length1 measurement (cm)", example=23.2)
    length2: float = Field(..., description="Length2 measurement (cm)", example=25.4)
    length3: float = Field(..., description="Length3 measurement (cm)", example=30.0)
    height: float = Field(..., description="Height measurement (cm)", example=11.52)
    width: float = Field(..., description="Width measurement (cm)", example=4.02)

class FishBatchInput(BaseModel):
    fish_list: List[FishInput] = Field(..., description="List of fish to predict")

class PredictionOutput(BaseModel):
    species: str
    predicted_weight: float
    confidence_interval_lower: Optional[float] = None
    confidence_interval_upper: Optional[float] = None
    features_used: dict
    prediction_timestamp: str

class BatchPredictionOutput(BaseModel):
    predictions: List[PredictionOutput]
    batch_size: int
    total_processing_time: float

class HealthCheck(BaseModel):
    status: str
    model_loaded: bool
    api_version: str
    available_species: List[str]

def load_model_and_encoder():
    """Load the trained model and label encoder"""
    global model, label_encoder
    
    try:
        # Try to load from MLflow model registry first
        try:
            model = mlflow.sklearn.load_model("models:/fish_weight_predictor/latest")
            logger.info("Model loaded from MLflow registry")
        except Exception as e:
            logger.warning(f"Failed to load from MLflow registry: {str(e)}")
            # Fallback to local file
            local_model_path = "models/best_fish_weight_model.pkl"
            if os.path.exists(local_model_path):
                model = joblib.load(local_model_path)
                logger.info("Model loaded from local file")
            else:
                raise Exception("No model found")
        
        # Setup label encoder
        if os.path.exists('Dataset/Fish.csv'):
            df = pd.read_csv('Dataset/Fish.csv')
            label_encoder = LabelEncoder()
            label_encoder.fit(df['Species'])
            logger.info(f"Label encoder setup with species: {list(label_encoder.classes_)}")
        else:
            # Default species
            label_encoder = LabelEncoder()
            label_encoder.classes_ = np.array(['Bream', 'Roach', 'Whitefish', 'Parkki', 'Perch', 'Pike', 'Smelt'])
            logger.warning("Using default species encoding")
        
        logger.info("Model and encoder loaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error loading model and encoder: {str(e)}")
        return False

def prepare_features(fish_data: FishInput):
    """Prepare features from input data"""
    try:
        # Convert to dictionary
        data = {
            'Species': fish_data.species,
            'Length1': fish_data.length1,
            'Length2': fish_data.length2,
            'Length3': fish_data.length3,
            'Height': fish_data.height,
            'Width': fish_data.width
        }
        
        # Create DataFrame
        df = pd.DataFrame([data])
        
        # Feature engineering
        df['Length_avg'] = (df['Length1'] + df['Length2'] + df['Length3']) / 3
        df['Volume_proxy'] = df['Length_avg'] * df['Height'] * df['Width']
        df['Length_diff'] = df['Length3'] - df['Length1']
        df['Aspect_ratio'] = df['Length_avg'] / df['Height']
        df['Body_index'] = df['Height'] / df['Width']
        
        # Encode species
        if label_encoder is not None:
            try:
                df['Species_encoded'] = label_encoder.transform(df['Species'])
            except ValueError:
                # Unknown species, use most common (first class)
                df['Species_encoded'] = 0
                logger.warning(f"Unknown species '{fish_data.species}', using default encoding")
        else:
            df['Species_encoded'] = 0
        
        # Select feature columns
        feature_columns = ['Length1', 'Length2', 'Length3', 'Height', 'Width', 
                         'Length_avg', 'Volume_proxy', 'Length_diff', 'Aspect_ratio', 
                         'Body_index', 'Species_encoded']
        
        return df[feature_columns], df[feature_columns].iloc[0].to_dict()
        
    except Exception as e:
        logger.error(f"Error preparing features: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error preparing features: {str(e)}")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Load model and encoder on startup"""
    if not load_model_and_encoder():
        logger.error("Failed to load model and encoder on startup")

# API Endpoints
@app.get("/", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    available_species = list(label_encoder.classes_) if label_encoder is not None else []
    
    return HealthCheck(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        api_version="1.0.0",
        available_species=available_species
    )

@app.post("/predict", response_model=PredictionOutput)
async def predict_fish_weight(fish: FishInput):
    """Predict fish weight for a single fish"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Prepare features
        X, features_dict = prepare_features(fish)
        
        # Make prediction
        prediction = model.predict(X)[0]
        
        # Calculate confidence interval (simplified bootstrap approach)
        predictions = []
        for _ in range(50):  # Reduced for API performance
            noise = np.random.normal(0, 0.03, X.shape)
            X_noisy = X + noise
            pred = model.predict(X_noisy)[0]
            predictions.append(pred)
        
        predictions = np.array(predictions)
        lower_ci = np.percentile(predictions, 2.5)
        upper_ci = np.percentile(predictions, 97.5)
        
        return PredictionOutput(
            species=fish.species,
            predicted_weight=float(prediction),
            confidence_interval_lower=float(lower_ci),
            confidence_interval_upper=float(upper_ci),
            features_used=features_dict,
            prediction_timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict/batch", response_model=BatchPredictionOutput)
async def predict_fish_weight_batch(batch: FishBatchInput):
    """Predict fish weight for multiple fish"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    start_time = datetime.now()
    predictions = []
    
    try:
        for fish in batch.fish_list:
            # Prepare features
            X, features_dict = prepare_features(fish)
            
            # Make prediction
            prediction = model.predict(X)[0]
            
            # Simplified confidence interval for batch processing
            noise_factor = 0.05  # 5% uncertainty
            lower_ci = prediction * (1 - noise_factor)
            upper_ci = prediction * (1 + noise_factor)
            
            predictions.append(PredictionOutput(
                species=fish.species,
                predicted_weight=float(prediction),
                confidence_interval_lower=float(lower_ci),
                confidence_interval_upper=float(upper_ci),
                features_used=features_dict,
                prediction_timestamp=datetime.now().isoformat()
            ))
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return BatchPredictionOutput(
            predictions=predictions,
            batch_size=len(batch.fish_list),
            total_processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error during batch prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")

@app.get("/species")
async def get_available_species():
    """Get list of available fish species"""
    if label_encoder is None:
        raise HTTPException(status_code=503, detail="Label encoder not loaded")
    
    return {
        "available_species": list(label_encoder.classes_),
        "total_species": len(label_encoder.classes_)
    }

@app.get("/model/info")
async def get_model_info():
    """Get information about the loaded model"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        model_info = {
            "model_type": type(model.named_steps['regressor']).__name__,
            "has_scaler": "scaler" in model.named_steps,
            "feature_count": len(['Length1', 'Length2', 'Length3', 'Height', 'Width', 
                                'Length_avg', 'Volume_proxy', 'Length_diff', 'Aspect_ratio', 
                                'Body_index', 'Species_encoded']),
            "features": ['Length1', 'Length2', 'Length3', 'Height', 'Width', 
                        'Length_avg', 'Volume_proxy', 'Length_diff', 'Aspect_ratio', 
                        'Body_index', 'Species_encoded']
        }
        
        # Add coefficient information for linear models
        if hasattr(model.named_steps['regressor'], 'coef_'):
            model_info["coefficients"] = model.named_steps['regressor'].coef_.tolist()
            model_info["intercept"] = float(model.named_steps['regressor'].intercept_)
        
        return model_info
        
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")

# cURL examples endpoint
@app.get("/examples/curl")
async def get_curl_examples():
    """Get cURL examples for using the API"""
    base_url = "http://localhost:8000"
    
    examples = {
        "health_check": f"curl -X GET '{base_url}/'",
        "single_prediction": f"""curl -X POST '{base_url}/predict' \\
-H 'Content-Type: application/json' \\
-d '{{
  "species": "Bream",
  "length1": 23.2,
  "length2": 25.4,
  "length3": 30.0,
  "height": 11.52,
  "width": 4.02
}}'""",
        "batch_prediction": f"""curl -X POST '{base_url}/predict/batch' \\
-H 'Content-Type: application/json' \\
-d '{{
  "fish_list": [
    {{
      "species": "Bream",
      "length1": 23.2,
      "length2": 25.4,
      "length3": 30.0,
      "height": 11.52,
      "width": 4.02
    }},
    {{
      "species": "Perch",
      "length1": 18.7,
      "length2": 20.0,
      "length3": 22.2,
      "height": 8.54,
      "width": 2.56
    }}
  ]
}}'""",
        "get_species": f"curl -X GET '{base_url}/species'",
        "model_info": f"curl -X GET '{base_url}/model/info'"
    }
    
    return examples

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "serve_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
