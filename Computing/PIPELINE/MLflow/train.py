#!/usr/bin/env python3
"""
MLflow Training Pipeline for Fish Weight Prediction
This script implements Linear Regression with MLflow tracking and model registry.
"""

import pandas as pd
import numpy as np
import os
import logging
import click
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FishWeightTrainer:
    def __init__(self, test_size=0.2, random_state=42, alpha=1.0):
        self.test_size = test_size
        self.random_state = random_state
        self.alpha = alpha
        self.models = {}
        self.best_model = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
    def load_processed_data(self, data_path='processed_data'):
        """Load preprocessed data"""
        try:
            if os.path.exists(f'{data_path}/features.csv') and os.path.exists(f'{data_path}/target.csv'):
                X = pd.read_csv(f'{data_path}/features.csv')
                y = pd.read_csv(f'{data_path}/target.csv').squeeze()
                logger.info(f"Loaded preprocessed data: X shape {X.shape}, y shape {y.shape}")
                return X, y
            else:
                # Fallback to original dataset
                logger.info("Preprocessed data not found, loading original dataset...")
                return self.load_original_data()
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return None, None
    
    def load_original_data(self):
        """Load and preprocess original dataset"""
        data_path = 'Dataset/Fish.csv'
        if not os.path.exists(data_path):
            logger.error(f"Dataset not found at {data_path}")
            return None, None
        
        df = pd.read_csv(data_path)
        
        # Basic preprocessing
        df = df.dropna()
        
        # Feature engineering
        df['Length_avg'] = (df['Length1'] + df['Length2'] + df['Length3']) / 3
        df['Volume_proxy'] = df['Length_avg'] * df['Height'] * df['Width']
        df['Length_diff'] = df['Length3'] - df['Length1']
        df['Aspect_ratio'] = df['Length_avg'] / df['Height']
        df['Body_index'] = df['Height'] / df['Width']
        
        # Encode species
        from sklearn.preprocessing import LabelEncoder
        le = LabelEncoder()
        df['Species_encoded'] = le.fit_transform(df['Species'])
        
        # Prepare features and target
        feature_columns = ['Length1', 'Length2', 'Length3', 'Height', 'Width', 
                          'Length_avg', 'Volume_proxy', 'Length_diff', 'Aspect_ratio', 
                          'Body_index', 'Species_encoded']
        X = df[feature_columns]
        y = df['Weight']
        
        return X, y
    
    def split_data(self, X, y):
        """Split data into training and testing sets"""
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=self.test_size, random_state=self.random_state
        )
        
        logger.info(f"Data split - Train: {self.X_train.shape}, Test: {self.X_test.shape}")
        
        # Log data split information
        mlflow.log_param("train_size", len(self.X_train))
        mlflow.log_param("test_size", len(self.X_test))
        mlflow.log_param("test_ratio", self.test_size)
        
    def create_models(self):
        """Create different regression models to compare"""
        self.models = {
            'linear_regression': Pipeline([
                ('scaler', StandardScaler()),
                ('regressor', LinearRegression())
            ]),
            'ridge_regression': Pipeline([
                ('scaler', StandardScaler()),
                ('regressor', Ridge(alpha=self.alpha, random_state=self.random_state))
            ]),
            'lasso_regression': Pipeline([
                ('scaler', StandardScaler()),
                ('regressor', Lasso(alpha=self.alpha, random_state=self.random_state))
            ]),
            'elastic_net': Pipeline([
                ('scaler', StandardScaler()),
                ('regressor', ElasticNet(alpha=self.alpha, random_state=self.random_state))
            ]),
            'random_forest': Pipeline([
                ('scaler', StandardScaler()),
                ('regressor', RandomForestRegressor(n_estimators=100, random_state=self.random_state))
            ])
        }
        
        logger.info(f"Created {len(self.models)} models for comparison")
    
    def train_and_evaluate_models(self):
        """Train and evaluate all models"""
        results = {}
        
        for name, model in self.models.items():
            logger.info(f"Training {name}...")
            
            # Train the model
            model.fit(self.X_train, self.y_train)
            
            # Make predictions
            y_pred_train = model.predict(self.X_train)
            y_pred_test = model.predict(self.X_test)
            
            # Calculate metrics
            train_mse = mean_squared_error(self.y_train, y_pred_train)
            test_mse = mean_squared_error(self.y_test, y_pred_test)
            train_r2 = r2_score(self.y_train, y_pred_train)
            test_r2 = r2_score(self.y_test, y_pred_test)
            test_mae = mean_absolute_error(self.y_test, y_pred_test)
            
            # Cross-validation
            cv_scores = cross_val_score(model, self.X_train, self.y_train, cv=5, 
                                      scoring='neg_mean_squared_error')
            cv_rmse = np.sqrt(-cv_scores.mean())
            
            results[name] = {
                'train_mse': train_mse,
                'test_mse': test_mse,
                'train_r2': train_r2,
                'test_r2': test_r2,
                'test_mae': test_mae,
                'cv_rmse': cv_rmse,
                'model': model
            }
            
            logger.info(f"{name} - Test R²: {test_r2:.4f}, Test RMSE: {np.sqrt(test_mse):.4f}")
        
        return results
    
    def select_best_model(self, results):
        """Select the best model based on test R² score"""
        best_model_name = max(results.keys(), key=lambda k: results[k]['test_r2'])
        self.best_model = results[best_model_name]['model']
        
        logger.info(f"Best model: {best_model_name} with R² = {results[best_model_name]['test_r2']:.4f}")
        
        return best_model_name, results[best_model_name]
    
    def create_evaluation_plots(self, best_model_name, results):
        """Create evaluation plots"""
        os.makedirs('evaluation_plots', exist_ok=True)
        
        # 1. Model comparison plot
        plt.figure(figsize=(12, 8))
        
        models = list(results.keys())
        r2_scores = [results[model]['test_r2'] for model in models]
        rmse_scores = [np.sqrt(results[model]['test_mse']) for model in models]
        
        x = np.arange(len(models))
        width = 0.35
        
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        color = 'tab:blue'
        ax1.set_xlabel('Models')
        ax1.set_ylabel('R² Score', color=color)
        bars1 = ax1.bar(x - width/2, r2_scores, width, label='R² Score', color=color, alpha=0.7)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.set_ylim(0, 1)
        
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('RMSE', color=color)
        bars2 = ax2.bar(x + width/2, rmse_scores, width, label='RMSE', color=color, alpha=0.7)
        ax2.tick_params(axis='y', labelcolor=color)
        
        plt.title('Model Performance Comparison')
        plt.xticks(x, models, rotation=45)
        
        # Highlight best model
        best_idx = models.index(best_model_name)
        bars1[best_idx].set_color('green')
        bars1[best_idx].set_alpha(1.0)
        
        plt.tight_layout()
        plt.savefig('evaluation_plots/model_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Actual vs Predicted plot for best model
        y_pred = self.best_model.predict(self.X_test)
        
        plt.figure(figsize=(10, 8))
        plt.scatter(self.y_test, y_pred, alpha=0.6)
        plt.plot([self.y_test.min(), self.y_test.max()], [self.y_test.min(), self.y_test.max()], 'r--', lw=2)
        plt.xlabel('Actual Weight (g)')
        plt.ylabel('Predicted Weight (g)')
        plt.title(f'Actual vs Predicted Weight - {best_model_name}')
        plt.text(0.05, 0.95, f'R² = {results[best_model_name]["test_r2"]:.4f}', 
                transform=plt.gca().transAxes, fontsize=12, bbox=dict(boxstyle="round", facecolor='wheat'))
        plt.tight_layout()
        plt.savefig('evaluation_plots/actual_vs_predicted.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Residuals plot
        residuals = self.y_test - y_pred
        
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        plt.scatter(y_pred, residuals, alpha=0.6)
        plt.axhline(y=0, color='r', linestyle='--')
        plt.xlabel('Predicted Weight (g)')
        plt.ylabel('Residuals')
        plt.title('Residuals vs Predicted')
        
        plt.subplot(1, 2, 2)
        plt.hist(residuals, bins=30, alpha=0.7)
        plt.xlabel('Residuals')
        plt.ylabel('Frequency')
        plt.title('Residuals Distribution')
        
        plt.tight_layout()
        plt.savefig('evaluation_plots/residuals_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info("Evaluation plots created successfully")
    
    def log_to_mlflow(self, best_model_name, best_results, all_results):
        """Log metrics, parameters, and model to MLflow"""
        # Log parameters
        mlflow.log_param("model_type", best_model_name)
        mlflow.log_param("test_size", self.test_size)
        mlflow.log_param("random_state", self.random_state)
        mlflow.log_param("alpha", self.alpha)
        mlflow.log_param("n_features", self.X_train.shape[1])
        
        # Log metrics for best model
        mlflow.log_metric("train_mse", best_results['train_mse'])
        mlflow.log_metric("test_mse", best_results['test_mse'])
        mlflow.log_metric("train_r2", best_results['train_r2'])
        mlflow.log_metric("test_r2", best_results['test_r2'])
        mlflow.log_metric("test_mae", best_results['test_mae'])
        mlflow.log_metric("cv_rmse", best_results['cv_rmse'])
        mlflow.log_metric("test_rmse", np.sqrt(best_results['test_mse']))
        
        # Log metrics for all models
        for model_name, results in all_results.items():
            mlflow.log_metric(f"{model_name}_r2", results['test_r2'])
            mlflow.log_metric(f"{model_name}_rmse", np.sqrt(results['test_mse']))
        
        # Log model
        mlflow.sklearn.log_model(
            self.best_model, 
            "fish_weight_predictor",
            registered_model_name="fish_weight_predictor"
        )
        
        # Log artifacts
        mlflow.log_artifacts("evaluation_plots", "evaluation_plots")
        
        logger.info("Results logged to MLflow successfully")

@click.command()
@click.option('--test_size', default=0.2, type=float, help='Test set size ratio')
@click.option('--random_state', default=42, type=int, help='Random state for reproducibility')
@click.option('--alpha', default=1.0, type=float, help='Regularization strength for Ridge/Lasso')
def main(test_size, random_state, alpha):
    """Main training pipeline"""
    
    with mlflow.start_run(run_name=f"fish_weight_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        
        # Initialize trainer
        trainer = FishWeightTrainer(test_size=test_size, random_state=random_state, alpha=alpha)
        
        # Load data
        X, y = trainer.load_processed_data()
        if X is None or y is None:
            logger.error("Failed to load data")
            return
        
        # Split data
        trainer.split_data(X, y)
        
        # Create models
        trainer.create_models()
        
        # Train and evaluate models
        results = trainer.train_and_evaluate_models()
        
        # Select best model
        best_model_name, best_results = trainer.select_best_model(results)
        
        # Create evaluation plots
        trainer.create_evaluation_plots(best_model_name, results)
        
        # Log to MLflow
        trainer.log_to_mlflow(best_model_name, best_results, results)
        
        # Save best model locally
        os.makedirs('models', exist_ok=True)
        joblib.dump(trainer.best_model, 'models/best_fish_weight_model.pkl')
        
        logger.info("Training pipeline completed successfully!")
        logger.info(f"Best model: {best_model_name}")
        logger.info(f"Test R²: {best_results['test_r2']:.4f}")
        logger.info(f"Test RMSE: {np.sqrt(best_results['test_mse']):.4f}")

if __name__ == "__main__":
    main()
