#!/usr/bin/env python3
"""
Fish Weight Prediction Model using Scikit-learn
This script trains a machine learning model to predict fish weight based on physical measurements.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

class FishWeightPredictor:
    def __init__(self, data_path='../data/Fish.csv'):
        """Initialize the Fish Weight Predictor"""
        self.data_path = data_path
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        
    def load_and_explore_data(self):
        """Load and explore the fish dataset"""
        print("Loading fish dataset...")
        
        # Try multiple possible paths for the dataset
        possible_paths = [
            self.data_path,
            '../data/Fish.csv',
            '../Dataset/Fish.csv',
            'data/Fish.csv',
            'Dataset/Fish.csv'
        ]
        
        self.df = None
        for path in possible_paths:
            if os.path.exists(path):
                self.df = pd.read_csv(path)
                print(f"Dataset loaded from: {path}")
                break
        
        if self.df is None:
            raise FileNotFoundError("Fish.csv not found in any expected location")
        
        print(f"Dataset shape: {self.df.shape}")
        print("\nDataset info:")
        print(self.df.info())
        print("\nFirst few rows:")
        print(self.df.head())
        print("\nStatistical summary:")
        print(self.df.describe())
        
        return self.df
    
    def preprocess_data(self):
        """Preprocess the data for training"""
        print("\nPreprocessing data...")
        
        # Handle missing values
        self.df = self.df.dropna()
        
        # Encode categorical variables (Species)
        if 'Species' in self.df.columns:
            species_encoded = pd.get_dummies(self.df['Species'], prefix='Species')
            self.df = pd.concat([self.df, species_encoded], axis=1)
            self.df = self.df.drop('Species', axis=1)
        
        # Define features and target
        # Assuming the target is 'Weight' and features are other numeric columns
        if 'Weight' in self.df.columns:
            self.target_column = 'Weight'
        else:
            # Find the weight-like column
            weight_cols = [col for col in self.df.columns if 'weight' in col.lower()]
            if weight_cols:
                self.target_column = weight_cols[0]
            else:
                raise ValueError("No weight column found in the dataset")
        
        # Select numeric features
        numeric_columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        self.feature_names = [col for col in numeric_columns if col != self.target_column]
        
        print(f"Target column: {self.target_column}")
        print(f"Feature columns: {self.feature_names}")
        
        # Prepare feature matrix and target vector
        self.X = self.df[self.feature_names]
        self.y = self.df[self.target_column]
        
        print(f"Features shape: {self.X.shape}")
        print(f"Target shape: {self.y.shape}")
        
    def train_models(self):
        """Train multiple models and compare performance"""
        print("\nSplitting data into train and test sets...")
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train models
        models = {
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'Linear Regression': LinearRegression()
        }
        
        results = {}
        
        for name, model in models.items():
            print(f"\nTraining {name}...")
            
            if name == 'Linear Regression':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            results[name] = {
                'model': model,
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'r2': r2,
                'y_pred': y_pred,
                'y_test': y_test
            }
            
            print(f"{name} Results:")
            print(f"  RMSE: {rmse:.2f}")
            print(f"  MAE: {mae:.2f}")
            print(f"  R² Score: {r2:.4f}")
        
        # Select best model based on R² score
        best_model_name = max(results.keys(), key=lambda k: results[k]['r2'])
        self.model = results[best_model_name]['model']
        
        print(f"\nBest model: {best_model_name} (R² = {results[best_model_name]['r2']:.4f})")
        
        return results
    
    def visualize_results(self, results):
        """Create visualizations of the results"""
        print("\nCreating visualizations...")
        
        # Create output directory
        os.makedirs('../output', exist_ok=True)
        
        # Model comparison
        plt.figure(figsize=(12, 8))
        
        # Subplot 1: Model Performance Comparison
        plt.subplot(2, 2, 1)
        models = list(results.keys())
        r2_scores = [results[model]['r2'] for model in models]
        plt.bar(models, r2_scores)
        plt.title('Model Performance Comparison (R² Score)')
        plt.ylabel('R² Score')
        plt.xticks(rotation=45)
        
        # Subplot 2: Feature Importance (for Random Forest)
        if 'Random Forest' in results:
            plt.subplot(2, 2, 2)
            rf_model = results['Random Forest']['model']
            feature_importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': rf_model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            plt.barh(feature_importance['feature'][:10], feature_importance['importance'][:10])
            plt.title('Top 10 Feature Importance (Random Forest)')
            plt.xlabel('Importance')
        
        # Subplot 3: Actual vs Predicted (best model)
        best_model_name = max(results.keys(), key=lambda k: results[k]['r2'])
        plt.subplot(2, 2, 3)
        y_test = results[best_model_name]['y_test']
        y_pred = results[best_model_name]['y_pred']
        plt.scatter(y_test, y_pred, alpha=0.6)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
        plt.xlabel('Actual Weight')
        plt.ylabel('Predicted Weight')
        plt.title(f'Actual vs Predicted ({best_model_name})')
        
        # Subplot 4: Residuals
        plt.subplot(2, 2, 4)
        residuals = y_test - y_pred
        plt.scatter(y_pred, residuals, alpha=0.6)
        plt.axhline(y=0, color='r', linestyle='--')
        plt.xlabel('Predicted Weight')
        plt.ylabel('Residuals')
        plt.title('Residual Plot')
        
        plt.tight_layout()
        plt.savefig('../output/fish_prediction_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Correlation heatmap
        plt.figure(figsize=(10, 8))
        correlation_matrix = self.df[self.feature_names + [self.target_column]].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title('Feature Correlation Matrix')
        plt.tight_layout()
        plt.savefig('../output/correlation_matrix.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def save_model(self):
        """Save the trained model and scaler"""
        print("\nSaving model and scaler...")
        
        os.makedirs('../models', exist_ok=True)
        
        # Save model
        joblib.dump(self.model, '../models/fish_weight_predictor.pkl')
        joblib.dump(self.scaler, '../models/feature_scaler.pkl')
        
        # Save feature names
        with open('../models/feature_names.txt', 'w') as f:
            f.write('\n'.join(self.feature_names))
        
        print("Model saved successfully!")
    
    def predict_fish_weight(self, measurements):
        """Predict fish weight for new measurements"""
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        # Convert to DataFrame if necessary
        if isinstance(measurements, dict):
            measurements = pd.DataFrame([measurements])
        
        # Ensure we have the right features
        measurements_scaled = self.scaler.transform(measurements)
        prediction = self.model.predict(measurements_scaled)
        
        return prediction[0] if len(prediction) == 1 else prediction

def main():
    """Main execution function"""
    print("Fish Weight Prediction Model")
    print("=" * 50)
    
    # Initialize predictor
    predictor = FishWeightPredictor()
    
    try:
        # Load and explore data
        predictor.load_and_explore_data()
        
        # Preprocess data
        predictor.preprocess_data()
        
        # Train models
        results = predictor.train_models()
        
        # Visualize results
        predictor.visualize_results(results)
        
        # Save model
        predictor.save_model()
        
        print("\n" + "=" * 50)
        print("Fish weight prediction model training completed successfully!")
        print("Model and visualizations saved to ../models and ../output directories")
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()