#!/usr/bin/env python3
"""
Inference Script for Fish Weight Prediction
This script loads a trained model and makes predictions on new data.
"""

import pandas as pd
import numpy as np
import os
import logging
import click
import mlflow
import mlflow.sklearn
import joblib
from sklearn.preprocessing import LabelEncoder

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FishWeightInference:
    def __init__(self, model_uri="models:/fish_weight_predictor/latest"):
        self.model_uri = model_uri
        self.model = None
        self.label_encoder = None
        
    def load_model(self):
        """Load the trained model from MLflow or local file"""
        try:
            # Try to load from MLflow model registry first
            if self.model_uri.startswith("models:/"):
                try:
                    self.model = mlflow.sklearn.load_model(self.model_uri)
                    logger.info(f"Model loaded from MLflow registry: {self.model_uri}")
                    return True
                except Exception as e:
                    logger.warning(f"Failed to load from MLflow registry: {str(e)}")
            
            # Fallback to local file
            local_model_path = "models/best_fish_weight_model.pkl"
            if os.path.exists(local_model_path):
                self.model = joblib.load(local_model_path)
                logger.info(f"Model loaded from local file: {local_model_path}")
                return True
            else:
                logger.error("No model found in MLflow registry or local file")
                return False
                
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def setup_label_encoder(self):
        """Setup label encoder for species encoding"""
        # Load original dataset to fit label encoder
        if os.path.exists('Dataset/Fish.csv'):
            df = pd.read_csv('Dataset/Fish.csv')
            self.label_encoder = LabelEncoder()
            self.label_encoder.fit(df['Species'])
            logger.info(f"Label encoder setup with species: {list(self.label_encoder.classes_)}")
        else:
            logger.warning("Original dataset not found, using default species encoding")
            # Default species mapping based on common fish types
            self.label_encoder = LabelEncoder()
            self.label_encoder.classes_ = np.array(['Bream', 'Roach', 'Whitefish', 'Parkki', 'Perch', 'Pike', 'Smelt'])
    
    def prepare_features(self, fish_data):
        """Prepare features from input data"""
        try:
            # Convert to DataFrame if it's a dictionary
            if isinstance(fish_data, dict):
                df = pd.DataFrame([fish_data])
            else:
                df = fish_data.copy()
            
            # Ensure all required columns are present
            required_base_columns = ['Species', 'Length1', 'Length2', 'Length3', 'Height', 'Width']
            
            for col in required_base_columns:
                if col not in df.columns:
                    raise ValueError(f"Missing required column: {col}")
            
            # Feature engineering (same as training)
            df['Length_avg'] = (df['Length1'] + df['Length2'] + df['Length3']) / 3
            df['Volume_proxy'] = df['Length_avg'] * df['Height'] * df['Width']
            df['Length_diff'] = df['Length3'] - df['Length1']
            df['Aspect_ratio'] = df['Length_avg'] / df['Height']
            df['Body_index'] = df['Height'] / df['Width']
            
            # Encode species
            if self.label_encoder is not None:
                df['Species_encoded'] = self.label_encoder.transform(df['Species'])
            else:
                df['Species_encoded'] = 0  # Default encoding
            
            # Select feature columns in the correct order
            feature_columns = ['Length1', 'Length2', 'Length3', 'Height', 'Width', 
                             'Length_avg', 'Volume_proxy', 'Length_diff', 'Aspect_ratio', 
                             'Body_index', 'Species_encoded']
            
            return df[feature_columns]
            
        except Exception as e:
            logger.error(f"Error preparing features: {str(e)}")
            return None
    
    def predict(self, fish_data):
        """Make weight predictions for fish data"""
        if self.model is None:
            logger.error("Model not loaded")
            return None
        
        # Prepare features
        X = self.prepare_features(fish_data)
        if X is None:
            return None
        
        try:
            # Make prediction
            predictions = self.model.predict(X)
            
            # If single prediction, return scalar
            if len(predictions) == 1:
                return float(predictions[0])
            
            return predictions.tolist()
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            return None
    
    def predict_with_confidence(self, fish_data, n_bootstrap=100):
        """Make predictions with confidence intervals using bootstrap"""
        if self.model is None:
            logger.error("Model not loaded")
            return None
        
        X = self.prepare_features(fish_data)
        if X is None:
            return None
        
        try:
            # Base prediction
            base_prediction = self.model.predict(X)
            
            # Bootstrap predictions for confidence interval
            # Note: This is a simplified approach, actual implementation would require
            # bootstrap sampling during training
            predictions = []
            for _ in range(n_bootstrap):
                # Add small random noise to simulate uncertainty
                noise = np.random.normal(0, 0.05, X.shape)
                X_noisy = X + noise
                pred = self.model.predict(X_noisy)
                predictions.append(pred)
            
            predictions = np.array(predictions)
            
            # Calculate confidence intervals
            lower_ci = np.percentile(predictions, 2.5, axis=0)
            upper_ci = np.percentile(predictions, 97.5, axis=0)
            
            result = {
                'prediction': base_prediction.tolist() if len(base_prediction) > 1 else float(base_prediction[0]),
                'confidence_interval_lower': lower_ci.tolist() if len(lower_ci) > 1 else float(lower_ci[0]),
                'confidence_interval_upper': upper_ci.tolist() if len(upper_ci) > 1 else float(upper_ci[0]),
                'confidence_level': 95
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error making prediction with confidence: {str(e)}")
            return None

def create_sample_predictions():
    """Create sample predictions for demonstration"""
    
    # Sample fish data for testing
    sample_fish = [
        {
            'Species': 'Bream',
            'Length1': 23.2,
            'Length2': 25.4,
            'Length3': 30.0,
            'Height': 11.52,
            'Width': 4.02
        },
        {
            'Species': 'Perch',
            'Length1': 18.7,
            'Length2': 20.0,
            'Length3': 22.2,
            'Height': 8.54,
            'Width': 2.56
        },
        {
            'Species': 'Pike',
            'Length1': 35.0,
            'Length2': 38.5,
            'Length3': 41.0,
            'Height': 9.85,
            'Width': 3.33
        }
    ]
    
    # Initialize inference engine
    inference_engine = FishWeightInference()
    
    # Load model and setup encoder
    if not inference_engine.load_model():
        return
    
    inference_engine.setup_label_encoder()
    
    logger.info("=== SAMPLE PREDICTIONS ===")
    
    for i, fish in enumerate(sample_fish, 1):
        logger.info(f"\\nFish {i}: {fish['Species']}")
        logger.info(f"  Measurements: L1={fish['Length1']}, L2={fish['Length2']}, L3={fish['Length3']}")
        logger.info(f"  Dimensions: H={fish['Height']}, W={fish['Width']}")
        
        # Simple prediction
        weight = inference_engine.predict(fish)
        if weight is not None:
            logger.info(f"  Predicted Weight: {weight:.2f} grams")
        
        # Prediction with confidence
        result = inference_engine.predict_with_confidence(fish)
        if result is not None:
            pred = result['prediction']
            lower = result['confidence_interval_lower']
            upper = result['confidence_interval_upper']
            logger.info(f"  Weight with 95% CI: {pred:.2f} grams [{lower:.2f}, {upper:.2f}]")

@click.command()
@click.option('--model_uri', default="models:/fish_weight_predictor/latest", 
              help='MLflow model URI or local model path')
@click.option('--species', default="Bream", help='Fish species')
@click.option('--length1', default=23.2, type=float, help='Length1 measurement')
@click.option('--length2', default=25.4, type=float, help='Length2 measurement')
@click.option('--length3', default=30.0, type=float, help='Length3 measurement')
@click.option('--height', default=11.52, type=float, help='Height measurement')
@click.option('--width', default=4.02, type=float, help='Width measurement')
@click.option('--confidence', is_flag=True, help='Include confidence intervals')
@click.option('--samples', is_flag=True, help='Run sample predictions')
def main(model_uri, species, length1, length2, length3, height, width, confidence, samples):
    """Main inference function"""
    
    with mlflow.start_run(run_name="fish_weight_inference"):
        
        if samples:
            create_sample_predictions()
            return
        
        # Initialize inference engine
        inference_engine = FishWeightInference(model_uri=model_uri)
        
        # Load model and setup encoder
        if not inference_engine.load_model():
            return
        
        inference_engine.setup_label_encoder()
        
        # Prepare input data
        fish_data = {
            'Species': species,
            'Length1': length1,
            'Length2': length2,
            'Length3': length3,
            'Height': height,
            'Width': width
        }
        
        logger.info(f"Making prediction for: {fish_data}")
        
        # Log input parameters
        mlflow.log_param("species", species)
        mlflow.log_param("length1", length1)
        mlflow.log_param("length2", length2)
        mlflow.log_param("length3", length3)
        mlflow.log_param("height", height)
        mlflow.log_param("width", width)
        
        if confidence:
            # Prediction with confidence intervals
            result = inference_engine.predict_with_confidence(fish_data)
            if result is not None:
                prediction = result['prediction']
                lower_ci = result['confidence_interval_lower']
                upper_ci = result['confidence_interval_upper']
                
                logger.info(f"Predicted Weight: {prediction:.2f} grams")
                logger.info(f"95% Confidence Interval: [{lower_ci:.2f}, {upper_ci:.2f}] grams")
                
                # Log results
                mlflow.log_metric("predicted_weight", prediction)
                mlflow.log_metric("confidence_interval_lower", lower_ci)
                mlflow.log_metric("confidence_interval_upper", upper_ci)
            
        else:
            # Simple prediction
            weight = inference_engine.predict(fish_data)
            if weight is not None:
                logger.info(f"Predicted Weight: {weight:.2f} grams")
                mlflow.log_metric("predicted_weight", weight)

if __name__ == "__main__":
    main()
