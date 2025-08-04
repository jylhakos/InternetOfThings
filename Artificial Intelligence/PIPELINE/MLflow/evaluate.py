#!/usr/bin/env python3
"""
Model Evaluation Script for Fish Weight Prediction
This script loads a trained model and performs comprehensive evaluation.
"""

import pandas as pd
import numpy as np
import os
import logging
import mlflow
import mlflow.sklearn
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelEvaluator:
    def __init__(self, model_path='models/best_fish_weight_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.X_test = None
        self.y_test = None
        
    def load_model(self):
        """Load the trained model"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                logger.info(f"Model loaded from {self.model_path}")
                return True
            else:
                logger.error(f"Model file not found at {self.model_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return False
    
    def load_test_data(self):
        """Load test data for evaluation"""
        try:
            # Try to load processed data first
            if os.path.exists('processed_data/features.csv'):
                X = pd.read_csv('processed_data/features.csv')
                y = pd.read_csv('processed_data/target.csv').squeeze()
                
                # Split using the same random state as training
                from sklearn.model_selection import train_test_split
                _, self.X_test, _, self.y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
                
                logger.info(f"Test data loaded: {self.X_test.shape}")
                return True
            else:
                logger.error("Processed data not found")
                return False
        except Exception as e:
            logger.error(f"Error loading test data: {str(e)}")
            return False
    
    def evaluate_model(self):
        """Evaluate the model performance"""
        if self.model is None or self.X_test is None:
            logger.error("Model or test data not loaded")
            return None
        
        # Make predictions
        y_pred = self.model.predict(self.X_test)
        
        # Calculate metrics
        mse = mean_squared_error(self.y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(self.y_test, y_pred)
        r2 = r2_score(self.y_test, y_pred)
        
        # Calculate additional metrics
        mape = np.mean(np.abs((self.y_test - y_pred) / self.y_test)) * 100
        residuals = self.y_test - y_pred
        std_residuals = np.std(residuals)
        
        evaluation_results = {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'mape': mape,
            'std_residuals': std_residuals,
            'predictions': y_pred,
            'residuals': residuals
        }
        
        logger.info(f"Evaluation Results:")
        logger.info(f"  R² Score: {r2:.4f}")
        logger.info(f"  RMSE: {rmse:.4f}")
        logger.info(f"  MAE: {mae:.4f}")
        logger.info(f"  MAPE: {mape:.2f}%")
        
        return evaluation_results
    
    def create_detailed_evaluation_plots(self, evaluation_results):
        """Create comprehensive evaluation visualizations"""
        os.makedirs('detailed_evaluation', exist_ok=True)
        
        y_pred = evaluation_results['predictions']
        residuals = evaluation_results['residuals']
        
        # 1. Actual vs Predicted with confidence bands
        plt.figure(figsize=(12, 8))
        plt.scatter(self.y_test, y_pred, alpha=0.6, s=50)
        
        # Perfect prediction line
        min_val = min(self.y_test.min(), y_pred.min())
        max_val = max(self.y_test.max(), y_pred.max())
        plt.plot([min_val, max_val], [min_val, max_val], 'r-', lw=2, label='Perfect Prediction')
        
        # Add confidence bands
        from scipy import stats
        slope, intercept, r_value, p_value, std_err = stats.linregress(self.y_test, y_pred)
        line = slope * self.y_test + intercept
        plt.plot(self.y_test, line, 'g--', alpha=0.8, label=f'Regression Line (R²={r_value**2:.3f})')
        
        plt.xlabel('Actual Weight (g)', fontsize=12)
        plt.ylabel('Predicted Weight (g)', fontsize=12)
        plt.title('Actual vs Predicted Weight with Regression Analysis', fontsize=14)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Add metrics text box
        metrics_text = f'R² = {evaluation_results["r2"]:.4f}\\nRMSE = {evaluation_results["rmse"]:.2f}\\nMAE = {evaluation_results["mae"]:.2f}'
        plt.text(0.05, 0.95, metrics_text, transform=plt.gca().transAxes, 
                fontsize=11, bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig('detailed_evaluation/actual_vs_predicted_detailed.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Residuals analysis
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Residuals vs Predicted
        axes[0,0].scatter(y_pred, residuals, alpha=0.6)
        axes[0,0].axhline(y=0, color='r', linestyle='--', alpha=0.8)
        axes[0,0].set_xlabel('Predicted Weight (g)')
        axes[0,0].set_ylabel('Residuals')
        axes[0,0].set_title('Residuals vs Predicted')
        axes[0,0].grid(True, alpha=0.3)
        
        # Residuals histogram
        axes[0,1].hist(residuals, bins=30, alpha=0.7, edgecolor='black')
        axes[0,1].axvline(x=0, color='r', linestyle='--', alpha=0.8)
        axes[0,1].set_xlabel('Residuals')
        axes[0,1].set_ylabel('Frequency')
        axes[0,1].set_title('Residuals Distribution')
        axes[0,1].grid(True, alpha=0.3)
        
        # Q-Q plot for residuals normality
        from scipy.stats import probplot
        probplot(residuals, dist="norm", plot=axes[1,0])
        axes[1,0].set_title('Q-Q Plot (Residuals Normality)')
        axes[1,0].grid(True, alpha=0.3)
        
        # Residuals vs Actual
        axes[1,1].scatter(self.y_test, residuals, alpha=0.6)
        axes[1,1].axhline(y=0, color='r', linestyle='--', alpha=0.8)
        axes[1,1].set_xlabel('Actual Weight (g)')
        axes[1,1].set_ylabel('Residuals')
        axes[1,1].set_title('Residuals vs Actual')
        axes[1,1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('detailed_evaluation/residuals_analysis_detailed.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Error analysis by weight ranges
        weight_ranges = pd.cut(self.y_test, bins=5, labels=['Very Light', 'Light', 'Medium', 'Heavy', 'Very Heavy'])
        error_by_range = pd.DataFrame({
            'weight_range': weight_ranges,
            'absolute_error': np.abs(residuals),
            'relative_error': np.abs(residuals) / self.y_test * 100
        })
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Absolute error by weight range
        error_by_range.boxplot(column='absolute_error', by='weight_range', ax=axes[0])
        axes[0].set_title('Absolute Error by Weight Range')
        axes[0].set_xlabel('Weight Range')
        axes[0].set_ylabel('Absolute Error (g)')
        
        # Relative error by weight range
        error_by_range.boxplot(column='relative_error', by='weight_range', ax=axes[1])
        axes[1].set_title('Relative Error by Weight Range')
        axes[1].set_xlabel('Weight Range')
        axes[1].set_ylabel('Relative Error (%)')
        
        plt.tight_layout()
        plt.savefig('detailed_evaluation/error_by_weight_range.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. Interactive plotly visualization
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Actual vs Predicted', 'Residuals vs Predicted', 
                          'Residuals Distribution', 'Error by Weight Range'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Actual vs Predicted
        fig.add_trace(
            go.Scatter(x=self.y_test, y=y_pred, mode='markers', name='Predictions',
                      opacity=0.6, marker=dict(size=5)),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=[self.y_test.min(), self.y_test.max()], 
                      y=[self.y_test.min(), self.y_test.max()],
                      mode='lines', name='Perfect Prediction', 
                      line=dict(color='red', dash='dash')),
            row=1, col=1
        )
        
        # Residuals vs Predicted
        fig.add_trace(
            go.Scatter(x=y_pred, y=residuals, mode='markers', name='Residuals',
                      opacity=0.6, marker=dict(size=5)),
            row=1, col=2
        )
        fig.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=2)
        
        # Residuals histogram
        fig.add_trace(
            go.Histogram(x=residuals, name='Residuals Dist', nbinsx=30),
            row=2, col=1
        )
        
        # Error metrics summary
        metrics_data = {
            'Metric': ['R²', 'RMSE', 'MAE', 'MAPE (%)'],
            'Value': [evaluation_results['r2'], evaluation_results['rmse'], 
                     evaluation_results['mae'], evaluation_results['mape']]
        }
        
        fig.add_trace(
            go.Table(
                header=dict(values=['Metric', 'Value'], fill_color='lightblue'),
                cells=dict(values=[metrics_data['Metric'], 
                                 [f'{v:.4f}' if v < 100 else f'{v:.2f}' for v in metrics_data['Value']]],
                          fill_color='lightgray')
            ),
            row=2, col=2
        )
        
        fig.update_layout(height=800, showlegend=True, 
                         title_text="Comprehensive Model Evaluation Dashboard")
        fig.write_html('detailed_evaluation/interactive_evaluation_dashboard.html')
        
        logger.info("Detailed evaluation plots created successfully")
    
    def create_feature_importance_analysis(self):
        """Analyze feature importance if the model supports it"""
        if hasattr(self.model.named_steps['regressor'], 'coef_'):
            # Linear model coefficients
            feature_names = ['Length1', 'Length2', 'Length3', 'Height', 'Width', 
                           'Length_avg', 'Volume_proxy', 'Length_diff', 'Aspect_ratio', 
                           'Body_index', 'Species_encoded']
            
            coefficients = self.model.named_steps['regressor'].coef_
            
            # Create feature importance plot
            plt.figure(figsize=(12, 8))
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': np.abs(coefficients)
            }).sort_values('importance', ascending=True)
            
            plt.barh(importance_df['feature'], importance_df['importance'])
            plt.xlabel('Absolute Coefficient Value')
            plt.title('Feature Importance (Linear Model Coefficients)')
            plt.tight_layout()
            plt.savefig('detailed_evaluation/feature_importance.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info("Feature importance analysis completed")
        
        elif hasattr(self.model.named_steps['regressor'], 'feature_importances_'):
            # Tree-based model feature importances
            feature_names = ['Length1', 'Length2', 'Length3', 'Height', 'Width', 
                           'Length_avg', 'Volume_proxy', 'Length_diff', 'Aspect_ratio', 
                           'Body_index', 'Species_encoded']
            
            importances = self.model.named_steps['regressor'].feature_importances_
            
            plt.figure(figsize=(12, 8))
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': importances
            }).sort_values('importance', ascending=True)
            
            plt.barh(importance_df['feature'], importance_df['importance'])
            plt.xlabel('Feature Importance')
            plt.title('Feature Importance (Tree-based Model)')
            plt.tight_layout()
            plt.savefig('detailed_evaluation/feature_importance.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info("Feature importance analysis completed")

def main():
    """Main evaluation pipeline"""
    with mlflow.start_run(run_name="model_evaluation"):
        
        # Initialize evaluator
        evaluator = ModelEvaluator()
        
        # Load model and test data
        if not evaluator.load_model():
            return
        
        if not evaluator.load_test_data():
            return
        
        # Evaluate model
        evaluation_results = evaluator.evaluate_model()
        if evaluation_results is None:
            return
        
        # Log metrics to MLflow
        mlflow.log_metric("eval_mse", evaluation_results['mse'])
        mlflow.log_metric("eval_rmse", evaluation_results['rmse'])
        mlflow.log_metric("eval_mae", evaluation_results['mae'])
        mlflow.log_metric("eval_r2", evaluation_results['r2'])
        mlflow.log_metric("eval_mape", evaluation_results['mape'])
        mlflow.log_metric("eval_std_residuals", evaluation_results['std_residuals'])
        
        # Create detailed evaluation plots
        evaluator.create_detailed_evaluation_plots(evaluation_results)
        
        # Feature importance analysis
        evaluator.create_feature_importance_analysis()
        
        # Log artifacts
        mlflow.log_artifacts("detailed_evaluation", "detailed_evaluation")
        
        logger.info("Model evaluation completed successfully!")

if __name__ == "__main__":
    main()
