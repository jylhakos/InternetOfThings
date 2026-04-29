#!/usr/bin/env python3
"""
Advanced Evaluation Module for RNN+LSTM Time-Series Forecasting
Comprehensive metrics and hyperparameter optimization for electricity consumption prediction
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

class TimeSeriesMetrics:
    """
    Comprehensive evaluation metrics for time-series forecasting models
    """
    
    @staticmethod
    def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Root Mean Squared Error"""
        return np.sqrt(mean_squared_error(y_true, y_pred))
    
    @staticmethod
    def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Mean Absolute Error"""
        return mean_absolute_error(y_true, y_pred)
    
    @staticmethod
    def mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Mean Absolute Percentage Error"""
        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    
    @staticmethod
    def smape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Symmetric Mean Absolute Percentage Error"""
        return 100 * np.mean(2 * np.abs(y_pred - y_true) / (np.abs(y_true) + np.abs(y_pred)))
    
    @staticmethod
    def mase(y_true: np.ndarray, y_pred: np.ndarray, y_train: np.ndarray, seasonality: int = 1) -> float:
        """Mean Absolute Scaled Error"""
        # Calculate naive forecast error (seasonal naive)
        naive_forecast = y_train[:-seasonality]
        naive_actual = y_train[seasonality:]
        mae_naive = np.mean(np.abs(naive_actual - naive_forecast))
        
        # Calculate MASE
        mae_forecast = np.mean(np.abs(y_true - y_pred))
        return mae_forecast / mae_naive if mae_naive != 0 else np.inf
    
    @staticmethod
    def directional_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Directional Accuracy - percentage of correct direction predictions"""
        if len(y_true) < 2:
            return 0.0
        
        true_direction = np.diff(y_true) > 0
        pred_direction = np.diff(y_pred) > 0
        return np.mean(true_direction == pred_direction) * 100
    
    @staticmethod
    def theil_u_statistic(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Theil's U-statistic for forecast accuracy"""
        numerator = np.sqrt(np.mean((y_pred - y_true) ** 2))
        denominator = np.sqrt(np.mean(y_true ** 2)) + np.sqrt(np.mean(y_pred ** 2))
        return numerator / denominator if denominator != 0 else np.inf

class ResidualsAnalysis:
    """
    Statistical analysis of prediction residuals
    """
    
    @staticmethod
    def ljung_box_test(residuals: np.ndarray, lags: int = 10) -> Tuple[float, float]:
        """
        Ljung-Box test for autocorrelation in residuals
        Returns: (test_statistic, p_value)
        """
        try:
            from statsmodels.stats.diagnostic import acorr_ljungbox
            result = acorr_ljungbox(residuals, lags=lags, return_df=False)
            return float(result[0][-1]), float(result[1][-1])  # Last lag statistics
        except ImportError:
            # Fallback implementation
            n = len(residuals)
            autocorrs = [np.corrcoef(residuals[:-i], residuals[i:])[0, 1] for i in range(1, lags + 1)]
            statistic = n * (n + 2) * sum([(autocorr ** 2) / (n - i) for i, autocorr in enumerate(autocorrs, 1)])
            p_value = 1 - stats.chi2.cdf(statistic, lags)
            return statistic, p_value
    
    @staticmethod
    def normality_test(residuals: np.ndarray) -> Tuple[float, float]:
        """
        Shapiro-Wilk test for normality of residuals
        Returns: (test_statistic, p_value)
        """
        if len(residuals) > 5000:  # Shapiro-Wilk has limitations for large samples
            # Use Kolmogorov-Smirnov test instead
            normalized_residuals = (residuals - np.mean(residuals)) / np.std(residuals)
            statistic, p_value = stats.kstest(normalized_residuals, 'norm')
        else:
            statistic, p_value = stats.shapiro(residuals)
        return statistic, p_value
    
    @staticmethod
    def durbin_watson_test(residuals: np.ndarray) -> float:
        """
        Durbin-Watson test for autocorrelation
        Values around 2 indicate no autocorrelation
        """
        diff_residuals = np.diff(residuals)
        return np.sum(diff_residuals ** 2) / np.sum(residuals ** 2)

class HyperparameterOptimizer:
    """
    Hyperparameter optimization for RNN/LSTM models using validation metrics
    """
    
    def __init__(self, model_class, param_grid: Dict[str, List], cv_splits: int = 5):
        self.model_class = model_class
        self.param_grid = param_grid
        self.cv_splits = cv_splits
        self.results = []
    
    def grid_search(self, X: np.ndarray, y: np.ndarray, metric: str = 'rmse') -> Dict[str, Any]:
        """
        Perform grid search with time-series cross-validation
        """
        from itertools import product
        
        # Generate all parameter combinations
        param_names = list(self.param_grid.keys())
        param_values = list(self.param_grid.values())
        param_combinations = list(product(*param_values))
        
        best_score = float('inf') if metric in ['rmse', 'mae', 'mape'] else float('-inf')
        best_params = None
        
        for i, params in enumerate(param_combinations):
            param_dict = dict(zip(param_names, params))
            
            # Perform time-series cross-validation
            cv_scores = self._time_series_cv(X, y, param_dict, metric)
            mean_score = np.mean(cv_scores)
            std_score = np.std(cv_scores)
            
            # Store results
            result = {
                'params': param_dict,
                'mean_score': mean_score,
                'std_score': std_score,
                'cv_scores': cv_scores,
                'rank': 0  # Will be set later
            }
            self.results.append(result)
            
            # Update best parameters
            is_better = (mean_score < best_score) if metric in ['rmse', 'mae', 'mape'] else (mean_score > best_score)
            if is_better:
                best_score = mean_score
                best_params = param_dict
            
            print(f"Combination {i+1}/{len(param_combinations)}: {param_dict} -> {metric}: {mean_score:.4f} (±{std_score:.4f})")
        
        # Rank results
        self.results.sort(key=lambda x: x['mean_score'], reverse=(metric not in ['rmse', 'mae', 'mape']))
        for i, result in enumerate(self.results):
            result['rank'] = i + 1
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'results': self.results
        }
    
    def _time_series_cv(self, X: np.ndarray, y: np.ndarray, params: Dict, metric: str) -> List[float]:
        """
        Perform time-series cross-validation
        """
        tscv = TimeSeriesSplit(n_splits=self.cv_splits)
        scores = []
        
        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            # Initialize and train model
            model = self.model_class(**params)
            model.fit(X_train, y_train)
            
            # Predict and evaluate
            y_pred = model.predict(X_val)
            
            # Calculate metric
            if metric == 'rmse':
                score = TimeSeriesMetrics.rmse(y_val, y_pred)
            elif metric == 'mae':
                score = TimeSeriesMetrics.mae(y_val, y_pred)
            elif metric == 'mape':
                score = TimeSeriesMetrics.mape(y_val, y_pred)
            elif metric == 'r2':
                score = r2_score(y_val, y_pred)
            else:
                raise ValueError(f"Unsupported metric: {metric}")
            
            scores.append(score)
        
        return scores

class ComprehensiveEvaluator:
    """
    Comprehensive evaluation framework for time-series forecasting models
    """
    
    def __init__(self):
        self.metrics = TimeSeriesMetrics()
        self.residuals_analyzer = ResidualsAnalysis()
    
    def evaluate_model(self, y_true: np.ndarray, y_pred: np.ndarray, 
                      y_train: np.ndarray = None) -> Dict[str, float]:
        """
        Comprehensive evaluation of model performance
        """
        evaluation_results = {}
        
        # Basic regression metrics
        evaluation_results['rmse'] = self.metrics.rmse(y_true, y_pred)
        evaluation_results['mae'] = self.metrics.mae(y_true, y_pred)
        evaluation_results['mape'] = self.metrics.mape(y_true, y_pred)
        evaluation_results['r2'] = r2_score(y_true, y_pred)
        
        # Time-series specific metrics
        evaluation_results['smape'] = self.metrics.smape(y_true, y_pred)
        evaluation_results['directional_accuracy'] = self.metrics.directional_accuracy(y_true, y_pred)
        evaluation_results['theil_u'] = self.metrics.theil_u_statistic(y_true, y_pred)
        
        if y_train is not None:
            evaluation_results['mase'] = self.metrics.mase(y_true, y_pred, y_train)
        
        # Residuals analysis
        residuals = y_true - y_pred
        ljung_box_stat, ljung_box_p = self.residuals_analyzer.ljung_box_test(residuals)
        evaluation_results['ljung_box_statistic'] = ljung_box_stat
        evaluation_results['ljung_box_p_value'] = ljung_box_p
        
        normality_stat, normality_p = self.residuals_analyzer.normality_test(residuals)
        evaluation_results['normality_statistic'] = normality_stat
        evaluation_results['normality_p_value'] = normality_p
        
        evaluation_results['durbin_watson'] = self.residuals_analyzer.durbin_watson_test(residuals)
        
        return evaluation_results
    
    def generate_evaluation_report(self, results: Dict[str, float], model_name: str = "Model") -> str:
        """
        Generate a comprehensive evaluation report
        """
        report = f"""
{'='*60}
{model_name.upper()} EVALUATION REPORT
{'='*60}

PERFORMANCE METRICS:
{'-'*30}
• RMSE (Root Mean Square Error):      {results['rmse']:.2f} MW
• MAE (Mean Absolute Error):          {results['mae']:.2f} MW
• MAPE (Mean Absolute Percentage Error): {results['mape']:.2f}%
• R² (Coefficient of Determination):  {results['r2']:.4f}
• sMAPE (Symmetric MAPE):             {results['smape']:.2f}%
• Directional Accuracy:               {results['directional_accuracy']:.2f}%
• Theil's U-statistic:                {results['theil_u']:.4f}

RESIDUALS ANALYSIS:
{'-'*30}
• Ljung-Box Test (Autocorrelation):
  - Statistic: {results['ljung_box_statistic']:.4f}
  - p-value: {results['ljung_box_p_value']:.4f}
  - Result: {'PASS' if results['ljung_box_p_value'] > 0.05 else 'FAIL'} (No significant autocorrelation)

• Normality Test (Shapiro-Wilk/KS):
  - Statistic: {results['normality_statistic']:.4f}
  - p-value: {results['normality_p_value']:.4f}
  - Result: {'PASS' if results['normality_p_value'] > 0.05 else 'FAIL'} (Residuals normally distributed)

• Durbin-Watson Test:
  - Statistic: {results['durbin_watson']:.4f}
  - Result: {'GOOD' if 1.5 <= results['durbin_watson'] <= 2.5 else 'POOR'} (Autocorrelation assessment)

INTERPRETATION:
{'-'*30}
• Model Accuracy: {'EXCELLENT' if results['mape'] < 5 else 'GOOD' if results['mape'] < 10 else 'MODERATE' if results['mape'] < 15 else 'POOR'}
• Variance Explained: {results['r2']*100:.1f}% of electricity consumption variance
• Direction Prediction: {'EXCELLENT' if results['directional_accuracy'] > 70 else 'GOOD' if results['directional_accuracy'] > 60 else 'MODERATE'}
"""
        
        if 'mase' in results:
            report += f"• MASE (Scaled Error vs Naive):       {results['mase']:.4f}\n"
        
        report += "\n" + "="*60
        
        return report
    
    def plot_evaluation_results(self, y_true: np.ndarray, y_pred: np.ndarray, 
                               model_name: str = "Model", save_path: str = None):
        """
        Create comprehensive evaluation plots
        """
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(f'{model_name} - Comprehensive Evaluation Analysis', fontsize=16)
        
        # 1. Actual vs Predicted
        axes[0, 0].scatter(y_true, y_pred, alpha=0.6)
        axes[0, 0].plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
        axes[0, 0].set_xlabel('Actual Values (MW)')
        axes[0, 0].set_ylabel('Predicted Values (MW)')
        axes[0, 0].set_title('Actual vs Predicted')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Residuals plot
        residuals = y_true - y_pred
        axes[0, 1].scatter(y_pred, residuals, alpha=0.6)
        axes[0, 1].axhline(y=0, color='r', linestyle='--')
        axes[0, 1].set_xlabel('Predicted Values (MW)')
        axes[0, 1].set_ylabel('Residuals (MW)')
        axes[0, 1].set_title('Residuals vs Predicted')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Residuals histogram
        axes[0, 2].hist(residuals, bins=30, density=True, alpha=0.7, edgecolor='black')
        axes[0, 2].set_xlabel('Residuals (MW)')
        axes[0, 2].set_ylabel('Density')
        axes[0, 2].set_title('Residuals Distribution')
        axes[0, 2].grid(True, alpha=0.3)
        
        # 4. Time series plot
        time_index = range(len(y_true))
        axes[1, 0].plot(time_index, y_true, label='Actual', linewidth=2)
        axes[1, 0].plot(time_index, y_pred, label='Predicted', linewidth=2)
        axes[1, 0].set_xlabel('Time Index')
        axes[1, 0].set_ylabel('Electricity Consumption (MW)')
        axes[1, 0].set_title('Time Series Comparison')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 5. Error over time
        absolute_errors = np.abs(residuals)
        axes[1, 1].plot(time_index, absolute_errors, linewidth=1)
        axes[1, 1].set_xlabel('Time Index')
        axes[1, 1].set_ylabel('Absolute Error (MW)')
        axes[1, 1].set_title('Prediction Error Over Time')
        axes[1, 1].grid(True, alpha=0.3)
        
        # 6. Q-Q plot for residuals normality
        from scipy.stats import probplot
        probplot(residuals, dist="norm", plot=axes[1, 2])
        axes[1, 2].set_title('Q-Q Plot (Residuals Normality)')
        axes[1, 2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Evaluation plots saved to: {save_path}")
        
        plt.show()

# Example usage function
def example_evaluation_pipeline():
    """
    Example of how to use the comprehensive evaluation framework
    """
    print("Comprehensive RNN+LSTM Evaluation Framework")
    print("="*50)
    
    # Generate sample data for demonstration
    np.random.seed(42)
    n_samples = 1000
    y_true = np.random.normal(15000, 2000, n_samples)  # Simulated electricity consumption
    noise = np.random.normal(0, 300, n_samples)
    y_pred = y_true + noise  # Simulated predictions with some error
    
    # Create evaluator
    evaluator = ComprehensiveEvaluator()
    
    # Perform evaluation
    results = evaluator.evaluate_model(y_true, y_pred)
    
    # Generate report
    report = evaluator.generate_evaluation_report(results, "LSTM Electricity Forecasting")
    print(report)
    
    # Create visualization
    evaluator.plot_evaluation_results(y_true, y_pred, "LSTM Model")
    
    return results

if __name__ == "__main__":
    # Run example evaluation
    example_evaluation_pipeline()
