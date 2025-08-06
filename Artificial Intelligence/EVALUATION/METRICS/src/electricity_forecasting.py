import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class LSTMModel(nn.Module):
    """
    LSTM Neural Network for time series forecasting
    """
    def __init__(self, input_size, hidden_size, num_layers, output_size, dropout=0.2):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           batch_first=True, dropout=dropout)
        
        # Dropout layer
        self.dropout = nn.Dropout(dropout)
        
        # Fully connected layer
        self.fc = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        # Initialize hidden and cell states
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        # Forward propagate LSTM
        out, _ = self.lstm(x, (h0, c0))
        
        # Apply dropout
        out = self.dropout(out)
        
        # Take the last output
        out = self.fc(out[:, -1, :])
        
        return out

class RNNModel(nn.Module):
    """
    Simple RNN Neural Network for time series forecasting
    """
    def __init__(self, input_size, hidden_size, num_layers, output_size, dropout=0.2):
        super(RNNModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # RNN layers
        self.rnn = nn.RNN(input_size, hidden_size, num_layers, 
                         batch_first=True, dropout=dropout)
        
        # Dropout layer
        self.dropout = nn.Dropout(dropout)
        
        # Fully connected layer
        self.fc = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        # Initialize hidden state
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        # Forward propagate RNN
        out, _ = self.rnn(x, h0)
        
        # Apply dropout
        out = self.dropout(out)
        
        # Take the last output
        out = self.fc(out[:, -1, :])
        
        return out

class ElectricityForecastModel:
    """
    Main class for electricity consumption forecasting using RNN/LSTM
    """
    def __init__(self, model_type='LSTM', sequence_length=24, hidden_size=64, 
                 num_layers=2, dropout=0.2, learning_rate=0.001):
        self.model_type = model_type
        self.sequence_length = sequence_length
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.dropout = dropout
        self.learning_rate = learning_rate
        
        # Scalers for normalization
        self.load_scaler = MinMaxScaler()
        self.temp_scaler = MinMaxScaler()
        
        # Model and device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.trained = False
        
    def load_data(self, electricity_path, temperature_path):
        """
        Load and preprocess electricity consumption and temperature data
        """
        print("Loading electricity consumption data...")
        # Load electricity data
        electricity_df = pd.read_csv(electricity_path)
        electricity_df['Date'] = pd.to_datetime(electricity_df['Date'], format='%d/%m/%Y %H:%M:%S')
        electricity_df = electricity_df.sort_values('Date')
        
        # Aggregate to daily data (taking mean of each day)
        electricity_daily = electricity_df.groupby(electricity_df['Date'].dt.date).agg({
            'Total Load [MW]': 'mean'
        }).reset_index()
        electricity_daily['Date'] = pd.to_datetime(electricity_daily['Date'])
        
        print("Loading temperature data...")
        # Load temperature data
        temp_df = pd.read_csv(temperature_path)
        temp_df['datetime'] = pd.to_datetime(temp_df['datetime'])
        temp_df = temp_df[['datetime', 'temp']].rename(columns={'datetime': 'Date'})
        
        # Merge datasets
        print("Merging datasets...")
        merged_df = pd.merge(electricity_daily, temp_df, on='Date', how='inner')
        merged_df = merged_df.sort_values('Date').reset_index(drop=True)
        
        # Add time-based features
        merged_df['day_of_year'] = merged_df['Date'].dt.dayofyear
        merged_df['month'] = merged_df['Date'].dt.month
        merged_df['season'] = merged_df['month'].apply(self._get_season)
        
        self.data = merged_df
        print(f"Dataset loaded: {len(merged_df)} daily records")
        return merged_df
    
    def _get_season(self, month):
        """Get season from month"""
        if month in [12, 1, 2]:
            return 0  # Winter
        elif month in [3, 4, 5]:
            return 1  # Spring
        elif month in [6, 7, 8]:
            return 2  # Summer
        else:
            return 3  # Autumn
    
    def prepare_sequences(self, train_ratio=0.8):
        """
        Prepare sequences for training and testing
        """
        # Normalize features
        load_values = self.data['Total Load [MW]'].values.reshape(-1, 1)
        temp_values = self.data['temp'].values.reshape(-1, 1)
        
        load_normalized = self.load_scaler.fit_transform(load_values)
        temp_normalized = self.temp_scaler.fit_transform(temp_values)
        
        # Add seasonal features (normalized)
        day_of_year = self.data['day_of_year'].values.reshape(-1, 1) / 365.0
        season_features = pd.get_dummies(self.data['season']).values
        
        # Combine features: [load, temperature, day_of_year, season_features]
        features = np.concatenate([
            load_normalized, 
            temp_normalized, 
            day_of_year, 
            season_features
        ], axis=1)
        
        # Create sequences
        X, y = [], []
        for i in range(self.sequence_length, len(features)):
            X.append(features[i-self.sequence_length:i])
            y.append(load_normalized[i, 0])  # Predict next day's load
        
        X, y = np.array(X), np.array(y)
        
        # Split into train and test
        train_size = int(len(X) * train_ratio)
        
        self.X_train = torch.FloatTensor(X[:train_size]).to(self.device)
        self.y_train = torch.FloatTensor(y[:train_size]).to(self.device)
        self.X_test = torch.FloatTensor(X[train_size:]).to(self.device)
        self.y_test = torch.FloatTensor(y[train_size:]).to(self.device)
        
        # Store feature size
        self.input_size = X.shape[2]
        
        print(f"Training sequences: {self.X_train.shape}")
        print(f"Testing sequences: {self.X_test.shape}")
        
        return self.X_train, self.y_train, self.X_test, self.y_test
    
    def build_model(self):
        """
        Build the neural network model
        """
        if self.model_type == 'LSTM':
            self.model = LSTMModel(
                input_size=self.input_size,
                hidden_size=self.hidden_size,
                num_layers=self.num_layers,
                output_size=1,
                dropout=self.dropout
            ).to(self.device)
        else:  # RNN
            self.model = RNNModel(
                input_size=self.input_size,
                hidden_size=self.hidden_size,
                num_layers=self.num_layers,
                output_size=1,
                dropout=self.dropout
            ).to(self.device)
        
        print(f"{self.model_type} model created with {sum(p.numel() for p in self.model.parameters())} parameters")
        return self.model
    
    def train_model(self, epochs=50, batch_size=32):
        """
        Train the model
        """
        if self.model is None:
            self.build_model()
        
        # Loss function and optimizer
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        
        # Training loop
        train_losses = []
        
        print(f"Training {self.model_type} model for {epochs} epochs...")
        
        for epoch in range(epochs):
            self.model.train()
            total_loss = 0
            
            # Mini-batch training
            for i in range(0, len(self.X_train), batch_size):
                batch_X = self.X_train[i:i+batch_size]
                batch_y = self.y_train[i:i+batch_size]
                
                # Forward pass
                outputs = self.model(batch_X)
                loss = criterion(outputs.squeeze(), batch_y)
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / (len(self.X_train) // batch_size + 1)
            train_losses.append(avg_loss)
            
            if (epoch + 1) % 10 == 0:
                print(f'Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.4f}')
        
        self.trained = True
        self.train_losses = train_losses
        print("Training completed!")
        
        return train_losses
    
    def evaluate_model(self):
        """
        Evaluate the model on test data
        """
        if not self.trained:
            raise ValueError("Model must be trained before evaluation")
        
        self.model.eval()
        with torch.no_grad():
            # Predictions on test set
            test_predictions = self.model(self.X_test)
            
            # Convert back to original scale
            test_pred_original = self.load_scaler.inverse_transform(
                test_predictions.cpu().numpy().reshape(-1, 1)
            ).flatten()
            
            test_actual_original = self.load_scaler.inverse_transform(
                self.y_test.cpu().numpy().reshape(-1, 1)
            ).flatten()
            
            # Calculate metrics
            mse = mean_squared_error(test_actual_original, test_pred_original)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(test_actual_original, test_pred_original)
            mape = np.mean(np.abs((test_actual_original - test_pred_original) / test_actual_original)) * 100
            
            self.test_metrics = {
                'MSE': mse,
                'RMSE': rmse,
                'MAE': mae,
                'MAPE': mape
            }
            
            self.test_predictions = test_pred_original
            self.test_actual = test_actual_original
            
            print("\nModel Evaluation Metrics:")
            print(f"MSE: {mse:.2f}")
            print(f"RMSE: {rmse:.2f} MW")
            print(f"MAE: {mae:.2f} MW")
            print(f"MAPE: {mape:.2f}%")
            
            return self.test_metrics
    
    def predict_next_day(self, last_sequence_data):
        """
        Predict electricity consumption for the next day
        """
        if not self.trained:
            raise ValueError("Model must be trained before prediction")
        
        self.model.eval()
        with torch.no_grad():
            # Ensure input is properly shaped and normalized
            if isinstance(last_sequence_data, np.ndarray):
                last_sequence_tensor = torch.FloatTensor(last_sequence_data).unsqueeze(0).to(self.device)
            else:
                last_sequence_tensor = last_sequence_data.unsqueeze(0)
            
            # Make prediction
            prediction = self.model(last_sequence_tensor)
            
            # Convert back to original scale
            prediction_original = self.load_scaler.inverse_transform(
                prediction.cpu().numpy().reshape(-1, 1)
            )[0, 0]
            
            return prediction_original
    
    def save_model(self, filepath):
        """
        Save the trained model
        """
        if not self.trained:
            raise ValueError("Model must be trained before saving")
        
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'model_type': self.model_type,
            'sequence_length': self.sequence_length,
            'hidden_size': self.hidden_size,
            'num_layers': self.num_layers,
            'input_size': self.input_size,
            'load_scaler': self.load_scaler,
            'temp_scaler': self.temp_scaler,
        }, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """
        Load a trained model
        """
        checkpoint = torch.load(filepath, map_location=self.device)
        
        self.model_type = checkpoint['model_type']
        self.sequence_length = checkpoint['sequence_length']
        self.hidden_size = checkpoint['hidden_size']
        self.num_layers = checkpoint['num_layers']
        self.input_size = checkpoint['input_size']
        self.load_scaler = checkpoint['load_scaler']
        self.temp_scaler = checkpoint['temp_scaler']
        
        # Build and load model
        self.build_model()
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.trained = True
        
        print(f"Model loaded from {filepath}")

if __name__ == "__main__":
    # Example usage
    print("Electricity Consumption Forecasting with RNN/LSTM")
    print("="*50)
    
    # Initialize model
    forecaster = ElectricityForecastModel(
        model_type='LSTM',  # or 'RNN'
        sequence_length=24,
        hidden_size=64,
        num_layers=2,
        dropout=0.2,
        learning_rate=0.001
    )
    
    # Load and prepare data
    data = forecaster.load_data(
        'Dataset/electrical-consumption-2024.csv',
        'Dataset/temperature-2024.csv'
    )
    
    # Prepare sequences
    X_train, y_train, X_test, y_test = forecaster.prepare_sequences(train_ratio=0.8)
    
    # Train model
    train_losses = forecaster.train_model(epochs=50, batch_size=32)
    
    # Evaluate model
    metrics = forecaster.evaluate_model()
    
    # Save model
    forecaster.save_model('lstm_electricity_model.pth')
    
    print("\nTraining and evaluation completed!")
