#!/usr/bin/env python3
"""
Model Optimization and Hyperparameter Tuning for RNN+LSTM Time-Series Forecasting
Advanced optimization techniques for electricity consumption prediction
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit
from advanced_evaluation import ComprehensiveEvaluator, TimeSeriesMetrics
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any, Optional
import time
import json
import warnings
warnings.filterwarnings('ignore')

class OptimizedLSTMModel(nn.Module):
    """
    Optimized LSTM model with advanced features for time-series forecasting
    """
    
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, 
                 output_size: int = 1, dropout: float = 0.2, 
                 bidirectional: bool = False, attention: bool = False):
        super(OptimizedLSTMModel, self).__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        self.attention = attention
        
        # LSTM layer
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True,
            bidirectional=bidirectional
        )
        
        # Attention mechanism (optional)
        if attention:
            lstm_output_size = hidden_size * 2 if bidirectional else hidden_size
            self.attention = nn.MultiheadAttention(
                embed_dim=lstm_output_size,
                num_heads=8,
                dropout=dropout,
                batch_first=True
            )
        
        # Output layers
        final_hidden_size = hidden_size * 2 if bidirectional else hidden_size
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(final_hidden_size, final_hidden_size // 2)
        self.fc2 = nn.Linear(final_hidden_size // 2, output_size)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        # LSTM forward pass
        lstm_out, (hidden, cell) = self.lstm(x)
        
        # Apply attention if enabled
        if self.attention:
            lstm_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
        
        # Use the last output for prediction
        last_output = lstm_out[:, -1, :]
        
        # Fully connected layers
        out = self.dropout(last_output)
        out = self.fc1(out)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)
        
        return out

class ModelOptimizer:
    """
    Advanced model optimization with hyperparameter tuning and early stopping
    """
    
    def __init__(self, device: Optional[torch.device] = None):
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.evaluator = ComprehensiveEvaluator()
        self.optimization_history = []
        
    def optimize_hyperparameters(self, X_train: np.ndarray, y_train: np.ndarray,
                                X_val: np.ndarray, y_val: np.ndarray,
                                search_space: Dict[str, List],
                                max_trials: int = 50,
                                optimization_metric: str = 'rmse') -> Dict[str, Any]:
        """
        Optimize hyperparameters using random search with early stopping
        """
        print(f"Starting hyperparameter optimization on {self.device}")
        print(f"Search space: {search_space}")
        print(f"Max trials: {max_trials}")
        print(f"Optimization metric: {optimization_metric}")
        print("="*60)
        
        best_score = float('inf') if optimization_metric in ['rmse', 'mae', 'mape'] else float('-inf')
        best_params = None
        best_model = None
        
        for trial in range(max_trials):
            # Sample random hyperparameters
            params = self._sample_hyperparameters(search_space)
            
            try:
                # Train model with current hyperparameters
                model, training_history = self._train_model_with_params(
                    X_train, y_train, X_val, y_val, params
                )
                
                # Evaluate model
                y_pred = self._predict(model, X_val)
                
                # Calculate optimization metric
                if optimization_metric == 'rmse':
                    score = TimeSeriesMetrics.rmse(y_val, y_pred)
                elif optimization_metric == 'mae':
                    score = TimeSeriesMetrics.mae(y_val, y_pred)
                elif optimization_metric == 'mape':
                    score = TimeSeriesMetrics.mape(y_val, y_pred)
                elif optimization_metric == 'r2':
                    from sklearn.metrics import r2_score
                    score = r2_score(y_val, y_pred)
                else:
                    raise ValueError(f"Unsupported metric: {optimization_metric}")
                
                # Store trial results
                trial_result = {
                    'trial': trial + 1,
                    'params': params,
                    'score': score,
                    'training_time': training_history['training_time'],
                    'epochs_trained': training_history['epochs_trained'],
                    'final_train_loss': training_history['final_train_loss'],
                    'final_val_loss': training_history['final_val_loss']
                }
                self.optimization_history.append(trial_result)
                
                # Check if this is the best model
                is_better = (score < best_score) if optimization_metric in ['rmse', 'mae', 'mape'] else (score > best_score)
                if is_better:
                    best_score = score
                    best_params = params.copy()
                    best_model = model
                
                print(f"Trial {trial + 1:3d}/{max_trials}: {optimization_metric}={score:.4f} - {params}")
                
            except Exception as e:
                print(f"Trial {trial + 1:3d}/{max_trials}: FAILED - {str(e)}")
                continue
        
        # Prepare optimization results
        optimization_results = {
            'best_params': best_params,
            'best_score': best_score,
            'best_model': best_model,
            'optimization_history': self.optimization_history,
            'total_trials': max_trials,
            'successful_trials': len(self.optimization_history)
        }
        
        print(f"\nOptimization completed!")
        print(f"Best {optimization_metric}: {best_score:.4f}")
        print(f"Best parameters: {best_params}")
        
        return optimization_results
    
    def _sample_hyperparameters(self, search_space: Dict[str, List]) -> Dict[str, Any]:
        """Sample random hyperparameters from search space"""
        params = {}
        for param_name, param_values in search_space.items():
            if isinstance(param_values[0], (int, float)) and len(param_values) == 2:
                # Continuous range [min, max]
                min_val, max_val = param_values
                if isinstance(min_val, int) and isinstance(max_val, int):
                    params[param_name] = np.random.randint(min_val, max_val + 1)
                else:
                    params[param_name] = np.random.uniform(min_val, max_val)
            else:
                # Discrete choices
                params[param_name] = np.random.choice(param_values)
        return params
    
    def _train_model_with_params(self, X_train: np.ndarray, y_train: np.ndarray,
                                X_val: np.ndarray, y_val: np.ndarray,
                                params: Dict[str, Any]) -> Tuple[nn.Module, Dict[str, Any]]:
        """Train model with given hyperparameters"""
        start_time = time.time()
        
        # Create model
        model = OptimizedLSTMModel(
            input_size=X_train.shape[2],
            hidden_size=params['hidden_size'],
            num_layers=params['num_layers'],
            dropout=params['dropout'],
            bidirectional=params.get('bidirectional', False),
            attention=params.get('attention', False)
        ).to(self.device)
        
        # Setup training
        criterion = nn.MSELoss()
        optimizer_name = params.get('optimizer', 'Adam')
        
        if optimizer_name == 'Adam':
            optimizer = optim.Adam(model.parameters(), lr=params['learning_rate'],
                                 weight_decay=params.get('weight_decay', 0))
        elif optimizer_name == 'RMSprop':
            optimizer = optim.RMSprop(model.parameters(), lr=params['learning_rate'])
        elif optimizer_name == 'SGD':
            optimizer = optim.SGD(model.parameters(), lr=params['learning_rate'],
                                momentum=params.get('momentum', 0.9))
        
        # Learning rate scheduler
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=10, verbose=False
        )
        
        # Prepare data loaders
        train_dataset = torch.utils.data.TensorDataset(
            torch.FloatTensor(X_train), torch.FloatTensor(y_train)
        )
        val_dataset = torch.utils.data.TensorDataset(
            torch.FloatTensor(X_val), torch.FloatTensor(y_val)
        )
        
        train_loader = torch.utils.data.DataLoader(
            train_dataset, batch_size=params['batch_size'], shuffle=True
        )
        val_loader = torch.utils.data.DataLoader(
            val_dataset, batch_size=params['batch_size'], shuffle=False
        )
        
        # Training loop with early stopping
        best_val_loss = float('inf')
        patience_counter = 0
        max_patience = params.get('patience', 15)
        max_epochs = params.get('max_epochs', 100)
        
        train_losses = []
        val_losses = []
        
        for epoch in range(max_epochs):
            # Training
            model.train()
            train_loss = 0.0
            for batch_X, batch_y in train_loader:
                batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)
                
                optimizer.zero_grad()
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y.unsqueeze(1))
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                
                optimizer.step()
                train_loss += loss.item()
            
            train_loss /= len(train_loader)
            
            # Validation
            model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)
                    outputs = model(batch_X)
                    loss = criterion(outputs, batch_y.unsqueeze(1))
                    val_loss += loss.item()
            
            val_loss /= len(val_loader)
            
            train_losses.append(train_loss)
            val_losses.append(val_loss)
            
            # Learning rate scheduling
            scheduler.step(val_loss)
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= max_patience:
                    break
        
        training_time = time.time() - start_time
        
        training_history = {
            'training_time': training_time,
            'epochs_trained': epoch + 1,
            'final_train_loss': train_losses[-1],
            'final_val_loss': val_losses[-1],
            'train_losses': train_losses,
            'val_losses': val_losses
        }
        
        return model, training_history
    
    def _predict(self, model: nn.Module, X: np.ndarray) -> np.ndarray:
        """Make predictions with the model"""
        model.eval()
        X_tensor = torch.FloatTensor(X).to(self.device)
        
        with torch.no_grad():
            predictions = model(X_tensor).cpu().numpy().flatten()
        
        return predictions
    
    def evaluate_optimized_model(self, model: nn.Module, X_test: np.ndarray, 
                                y_test: np.ndarray, y_train: np.ndarray = None) -> Dict[str, Any]:
        """Comprehensive evaluation of the optimized model"""
        y_pred = self._predict(model, X_test)
        
        # Basic evaluation
        evaluation_results = self.evaluator.evaluate_model(y_test, y_pred, y_train)
        
        # Additional analysis
        evaluation_results['prediction_std'] = np.std(y_pred)
        evaluation_results['residual_std'] = np.std(y_test - y_pred)
        evaluation_results['mean_prediction'] = np.mean(y_pred)
        evaluation_results['mean_actual'] = np.mean(y_test)
        
        return evaluation_results
    
    def plot_optimization_results(self, optimization_results: Dict[str, Any], 
                                 save_path: str = None):
        """Plot optimization results and trends"""
        history = optimization_results['optimization_history']
        if not history:
            print("No optimization history to plot")
            return
        
        # Convert to DataFrame for easier plotting
        df = pd.DataFrame(history)
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Hyperparameter Optimization Results', fontsize=16)
        
        # 1. Score over trials
        axes[0, 0].plot(df['trial'], df['score'], 'b-', alpha=0.7)
        axes[0, 0].axhline(y=optimization_results['best_score'], color='r', linestyle='--', 
                          label=f"Best: {optimization_results['best_score']:.4f}")
        axes[0, 0].set_xlabel('Trial')
        axes[0, 0].set_ylabel('Validation Score')
        axes[0, 0].set_title('Optimization Progress')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Training time vs score
        axes[0, 1].scatter(df['training_time'], df['score'], alpha=0.6)
        axes[0, 1].set_xlabel('Training Time (seconds)')
        axes[0, 1].set_ylabel('Validation Score')
        axes[0, 1].set_title('Training Time vs Performance')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Hidden size distribution
        if 'hidden_size' in df.columns:
            hidden_sizes = [params['hidden_size'] for params in df['params']]
            axes[0, 2].hist(hidden_sizes, bins=10, alpha=0.7, edgecolor='black')
            axes[0, 2].set_xlabel('Hidden Size')
            axes[0, 2].set_ylabel('Frequency')
            axes[0, 2].set_title('Hidden Size Distribution')
            axes[0, 2].grid(True, alpha=0.3)
        
        # 4. Learning rate vs score
        if 'learning_rate' in df.columns:
            learning_rates = [params['learning_rate'] for params in df['params']]
            axes[1, 0].scatter(learning_rates, df['score'], alpha=0.6)
            axes[1, 0].set_xlabel('Learning Rate')
            axes[1, 0].set_ylabel('Validation Score')
            axes[1, 0].set_title('Learning Rate vs Performance')
            axes[1, 0].set_xscale('log')
            axes[1, 0].grid(True, alpha=0.3)
        
        # 5. Epochs trained distribution
        axes[1, 1].hist(df['epochs_trained'], bins=15, alpha=0.7, edgecolor='black')
        axes[1, 1].set_xlabel('Epochs Trained')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].set_title('Training Duration Distribution')
        axes[1, 1].grid(True, alpha=0.3)
        
        # 6. Top 10 configurations
        top_configs = df.nsmallest(10, 'score') if 'rmse' in str(optimization_results) else df.nlargest(10, 'score')
        
        # Create a heatmap of top configurations
        config_features = []
        for _, row in top_configs.iterrows():
            params = row['params']
            config_features.append([
                params.get('hidden_size', 0),
                params.get('num_layers', 0),
                params.get('learning_rate', 0) * 1000,  # Scale for visualization
                params.get('dropout', 0) * 100,  # Scale for visualization
                params.get('batch_size', 0)
            ])
        
        if config_features:
            config_array = np.array(config_features)
            im = axes[1, 2].imshow(config_array.T, aspect='auto', cmap='viridis')
            axes[1, 2].set_xlabel('Top Configuration Rank')
            axes[1, 2].set_ylabel('Hyperparameter')
            axes[1, 2].set_title('Top 10 Configurations Heatmap')
            axes[1, 2].set_yticks(range(5))
            axes[1, 2].set_yticklabels(['Hidden Size', 'Num Layers', 'LR*1000', 'Dropout*100', 'Batch Size'])
            plt.colorbar(im, ax=axes[1, 2])
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Optimization plots saved to: {save_path}")
        
        plt.show()
    
    def save_optimization_results(self, optimization_results: Dict[str, Any], 
                                 filepath: str):
        """Save optimization results to JSON file"""
        # Prepare data for JSON serialization
        save_data = {
            'best_params': optimization_results['best_params'],
            'best_score': float(optimization_results['best_score']),
            'total_trials': optimization_results['total_trials'],
            'successful_trials': optimization_results['successful_trials'],
            'optimization_history': []
        }
        
        # Convert history to JSON-serializable format
        for trial in optimization_results['optimization_history']:
            trial_data = {
                'trial': trial['trial'],
                'params': trial['params'],
                'score': float(trial['score']),
                'training_time': float(trial['training_time']),
                'epochs_trained': int(trial['epochs_trained']),
                'final_train_loss': float(trial['final_train_loss']),
                'final_val_loss': float(trial['final_val_loss'])
            }
            save_data['optimization_history'].append(trial_data)
        
        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        print(f"Optimization results saved to: {filepath}")

def run_comprehensive_optimization():
    """
    Example comprehensive optimization pipeline
    """
    print("🚀 COMPREHENSIVE RNN+LSTM OPTIMIZATION PIPELINE")
    print("="*60)
    
    # Generate sample time-series data
    np.random.seed(42)
    n_samples = 2000
    sequence_length = 24
    n_features = 7
    
    # Create synthetic electricity consumption data
    time_trend = np.linspace(0, 4*np.pi, n_samples)
    seasonal_pattern = 2000 * np.sin(time_trend) + 1000 * np.sin(time_trend * 12)
    noise = np.random.normal(0, 500, n_samples)
    base_consumption = 15000 + seasonal_pattern + noise
    
    # Create feature matrix (load, temperature, day_of_year, etc.)
    features = np.random.randn(n_samples, n_features)
    features[:, 0] = base_consumption  # First feature is consumption
    
    # Create sequences
    X, y = [], []
    for i in range(sequence_length, n_samples):
        X.append(features[i-sequence_length:i])
        y.append(base_consumption[i])
    
    X = np.array(X)
    y = np.array(y)
    
    # Split data
    train_size = int(0.6 * len(X))
    val_size = int(0.2 * len(X))
    
    X_train = X[:train_size]
    y_train = y[:train_size]
    X_val = X[train_size:train_size + val_size]
    y_val = y[train_size:train_size + val_size]
    X_test = X[train_size + val_size:]
    y_test = y[train_size + val_size:]
    
    print(f"Training data shape: {X_train.shape}")
    print(f"Validation data shape: {X_val.shape}")
    print(f"Test data shape: {X_test.shape}")
    
    # Define search space
    search_space = {
        'hidden_size': [32, 64, 128, 256],
        'num_layers': [1, 2, 3, 4],
        'learning_rate': [0.0001, 0.001, 0.01],
        'dropout': [0.1, 0.2, 0.3, 0.4],
        'batch_size': [16, 32, 64],
        'optimizer': ['Adam', 'RMSprop'],
        'weight_decay': [0, 1e-5, 1e-4],
        'max_epochs': [50],
        'patience': [15]
    }
    
    # Create optimizer
    optimizer = ModelOptimizer()
    
    # Run optimization
    print("\n🔍 Starting hyperparameter optimization...")
    optimization_results = optimizer.optimize_hyperparameters(
        X_train, y_train, X_val, y_val,
        search_space=search_space,
        max_trials=20,  # Reduced for demo
        optimization_metric='rmse'
    )
    
    # Evaluate best model on test set
    print("\n📊 Evaluating best model on test set...")
    best_model = optimization_results['best_model']
    test_evaluation = optimizer.evaluate_optimized_model(
        best_model, X_test, y_test, y_train
    )
    
    # Generate comprehensive report
    evaluator = ComprehensiveEvaluator()
    report = evaluator.generate_evaluation_report(test_evaluation, "Optimized LSTM")
    print(report)
    
    # Plot results
    optimizer.plot_optimization_results(optimization_results, 'optimization_results.png')
    
    # Save results
    optimizer.save_optimization_results(optimization_results, 'optimization_results.json')
    
    return optimization_results, test_evaluation

if __name__ == "__main__":
    # Run comprehensive optimization
    opt_results, test_eval = run_comprehensive_optimization()
