import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from electricity_forecasting import ElectricityForecastModel
import warnings
warnings.filterwarnings('ignore')

def train_and_compare_models():
    """
    Train and compare RNN vs LSTM models for electricity forecasting
    """
    print("ELECTRICITY CONSUMPTION FORECASTING")
    print("Training and Comparing RNN vs LSTM Models")
    print("="*60)
    
    # Model configurations to test
    models_config = [
        {
            'name': 'Simple RNN',
            'model_type': 'RNN',
            'hidden_size': 64,
            'num_layers': 2,
            'learning_rate': 0.001
        },
        {
            'name': 'LSTM',
            'model_type': 'LSTM',
            'hidden_size': 64,
            'num_layers': 2,
            'learning_rate': 0.001
        },
        {
            'name': 'Deep LSTM',
            'model_type': 'LSTM',
            'hidden_size': 128,
            'num_layers': 3,
            'learning_rate': 0.0005
        }
    ]
    
    results = {}
    
    for config in models_config:
        print(f"\nTraining {config['name']} model...")
        print("-" * 40)
        
        # Initialize model
        model = ElectricityForecastModel(
            model_type=config['model_type'],
            sequence_length=24,
            hidden_size=config['hidden_size'],
            num_layers=config['num_layers'],
            dropout=0.2,
            learning_rate=config['learning_rate']
        )
        
        # Load and prepare data
        data = model.load_data(
            'Dataset/electrical-consumption-2024.csv',
            'Dataset/temperature-2024.csv'
        )
        
        # Prepare sequences
        X_train, y_train, X_test, y_test = model.prepare_sequences(train_ratio=0.8)
        
        # Train model (limited epochs for demonstration)
        train_losses = model.train_model(epochs=30, batch_size=32)
        
        # Evaluate model
        metrics = model.evaluate_model()
        
        # Store results
        results[config['name']] = {
            'model': model,
            'metrics': metrics,
            'train_losses': train_losses,
            'config': config
        }
        
        # Save model
        model_filename = f"{config['model_type'].lower()}_model_{config['hidden_size']}.pth"
        model.save_model(model_filename)
        
        print(f"✓ {config['name']} training completed!")
    
    return results

def visualize_results(results):
    """
    Visualize training results and model comparisons
    """
    print("\nCreating visualizations...")
    
    # 1. Training Loss Comparison
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    for name, result in results.items():
        plt.plot(result['train_losses'], label=name, linewidth=2)
    plt.title('Training Loss Comparison')
    plt.xlabel('Epoch')
    plt.ylabel('Loss (MSE)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 2. Metrics Comparison
    plt.subplot(1, 3, 2)
    models = list(results.keys())
    rmse_values = [results[model]['metrics']['RMSE'] for model in models]
    mae_values = [results[model]['metrics']['MAE'] for model in models]
    
    x = np.arange(len(models))
    width = 0.35
    
    plt.bar(x - width/2, rmse_values, width, label='RMSE', alpha=0.8)
    plt.bar(x + width/2, mae_values, width, label='MAE', alpha=0.8)
    plt.xlabel('Models')
    plt.ylabel('Error (MW)')
    plt.title('Model Performance Comparison')
    plt.xticks(x, models, rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 3. Prediction vs Actual (Best Model)
    best_model_name = min(results.keys(), key=lambda x: results[x]['metrics']['RMSE'])
    best_result = results[best_model_name]
    
    plt.subplot(1, 3, 3)
    actual = best_result['model'].test_actual[:50]  # First 50 test points
    predicted = best_result['model'].test_predictions[:50]
    
    plt.plot(actual, label='Actual', linewidth=2)
    plt.plot(predicted, label='Predicted', linewidth=2, alpha=0.8)
    plt.title(f'Predictions vs Actual ({best_model_name})')
    plt.xlabel('Time Steps')
    plt.ylabel('Electricity Load (MW)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('model_comparison_results.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 4. Detailed predictions plot
    plt.figure(figsize=(15, 8))
    
    for i, (name, result) in enumerate(results.items()):
        plt.subplot(len(results), 1, i+1)
        actual = result['model'].test_actual[:100]
        predicted = result['model'].test_predictions[:100]
        
        plt.plot(actual, label='Actual', color='blue', linewidth=1.5)
        plt.plot(predicted, label='Predicted', color='red', linewidth=1.5, alpha=0.7)
        plt.title(f'{name} - RMSE: {result["metrics"]["RMSE"]:.2f} MW')
        plt.ylabel('Load (MW)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if i == len(results) - 1:
            plt.xlabel('Time Steps (Days)')
    
    plt.tight_layout()
    plt.savefig('detailed_predictions.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_performance_report(results):
    """
    Create a detailed performance report
    """
    print("\n" + "="*60)
    print("MODEL PERFORMANCE REPORT")
    print("="*60)
    
    # Sort models by RMSE
    sorted_models = sorted(results.items(), key=lambda x: x[1]['metrics']['RMSE'])
    
    print(f"{'Model':<15} {'RMSE':<8} {'MAE':<8} {'MAPE':<8} {'Parameters':<12}")
    print("-" * 60)
    
    for name, result in sorted_models:
        metrics = result['metrics']
        config = result['config']
        
        # Calculate number of parameters (approximation)
        if config['model_type'] == 'LSTM':
            # LSTM has 4 gates, each with input_size + hidden_size + 1 parameters
            input_size = 7  # Approximate based on features
            hidden_size = config['hidden_size']
            num_layers = config['num_layers']
            params = num_layers * (4 * (input_size + hidden_size + 1) * hidden_size + hidden_size)
        else:  # RNN
            input_size = 7
            hidden_size = config['hidden_size']
            num_layers = config['num_layers']
            params = num_layers * ((input_size + hidden_size + 1) * hidden_size + hidden_size)
        
        print(f"{name:<15} {metrics['RMSE']:<8.1f} {metrics['MAE']:<8.1f} {metrics['MAPE']:<8.1f} {params:<12,}")
    
    # Best model analysis
    best_model_name, best_result = sorted_models[0]
    print(f"\n🏆 BEST MODEL: {best_model_name}")
    print(f"   • RMSE: {best_result['metrics']['RMSE']:.2f} MW")
    print(f"   • MAE: {best_result['metrics']['MAE']:.2f} MW") 
    print(f"   • MAPE: {best_result['metrics']['MAPE']:.2f}%")
    print(f"   • Architecture: {best_result['config']['model_type']}")
    print(f"   • Hidden Size: {best_result['config']['hidden_size']}")
    print(f"   • Layers: {best_result['config']['num_layers']}")
    
    # Seasonal performance analysis
    print(f"\n📊 SEASONAL PERFORMANCE ANALYSIS ({best_model_name}):")
    
    # Load the data to get seasonal information
    model = best_result['model']
    try:
        data = model.data
        
        # Get test period data
        train_size = int(len(data) * 0.8)
        test_data = data.iloc[train_size + model.sequence_length:]
        
        if len(test_data) > 0:
            seasonal_rmse = {}
            for season in ['Winter', 'Spring', 'Summer', 'Autumn']:
                season_mask = test_data['Season'] == season
                if season_mask.sum() > 0:
                    season_indices = season_mask[season_mask].index - (train_size + model.sequence_length)
                    season_indices = season_indices[season_indices < len(model.test_actual)]
                    
                    if len(season_indices) > 0:
                        season_actual = model.test_actual[season_indices]
                        season_pred = model.test_predictions[season_indices]
                        seasonal_rmse[season] = np.sqrt(mean_squared_error(season_actual, season_pred))
            
            for season, rmse in seasonal_rmse.items():
                print(f"   • {season}: {rmse:.2f} MW RMSE")
    except Exception as e:
        print(f"   • Seasonal analysis not available: {e}")
    
    return best_model_name, best_result

def demonstrate_forecasting(best_model_name, best_result):
    """
    Demonstrate forecasting capabilities
    """
    print(f"\n" + "="*60)
    print("FORECASTING DEMONSTRATION")
    print("="*60)
    
    model = best_result['model']
    
    # Simulate next day prediction
    print(f"Using {best_model_name} for next-day forecasting...")
    
    # Get the last sequence from test data
    last_sequence = model.X_test[-1:].cpu().numpy()
    
    # Make prediction
    prediction = model.predict_next_day(last_sequence)
    
    # Get actual last values for context
    last_actual = model.load_scaler.inverse_transform(
        model.y_test[-1:].cpu().numpy().reshape(-1, 1)
    )[0, 0]
    
    print(f"\n📈 FORECAST RESULTS:")
    print(f"   • Last observed load: {last_actual:.1f} MW")
    print(f"   • Predicted next day: {prediction:.1f} MW")
    print(f"   • Change: {prediction - last_actual:+.1f} MW ({((prediction - last_actual) / last_actual * 100):+.1f}%)")
    
    # Calculate confidence interval (simplified)
    recent_errors = np.abs(model.test_actual[-10:] - model.test_predictions[-10:])
    avg_error = np.mean(recent_errors)
    
    print(f"   • Confidence interval: {prediction - 1.96*avg_error:.1f} - {prediction + 1.96*avg_error:.1f} MW")
    print(f"   • Average recent error: ±{avg_error:.1f} MW")

def main():
    """
    Main function to run the complete training and evaluation
    """
    # Train and compare models
    results = train_and_compare_models()
    
    # Visualize results
    visualize_results(results)
    
    # Create performance report
    best_model_name, best_result = create_performance_report(results)
    
    # Demonstrate forecasting
    demonstrate_forecasting(best_model_name, best_result)
    
    print(f"\n" + "="*60)
    print("TRAINING COMPLETE!")
    print("="*60)
    print("Generated files:")
    print("• model_comparison_results.png")
    print("• detailed_predictions.png")
    print("• rnn_model_64.pth")
    print("• lstm_model_64.pth")
    print("• lstm_model_128.pth")
    print("\nNext steps:")
    print("1. Run the API server: python api_server.py")
    print("2. Test forecasting: curl commands in README.md")
    print("3. Analyze results with exploratory_data_analysis.py")

if __name__ == "__main__":
    main()
