# Configuration file for electricity forecasting models with weather integration

# Data Configuration
DATA_CONFIG = {
    'electricity_file': 'Dataset/electrical-consumption-2024.csv',
    'temperature_file': 'Dataset/temperature-2024.csv',
    'train_ratio': 0.8,
    'sequence_length': 24,  # Days to look back for prediction
}

# Weather Service Configuration
WEATHER_CONFIG = {
    'api_base_url': 'https://api.open-meteo.com/v1/forecast',
    'geocoding_service': 'nominatim',
    'user_agent': 'electricity_forecasting_lazio_italy',
    'default_city': 'Roma',
    'default_region': 'Lazio',
    'default_country': 'Italy',
    'default_coordinates': (41.9028, 12.4964),  # Roma, Lazio
    'request_timeout': 10,  # seconds
    'max_forecast_days': 7,
    'timezone': 'Europe/Rome',
    'supported_cities': [
        'Roma', 'Latina', 'Frosinone', 'Rieti', 'Viterbo',
        'Tivoli', 'Anzio', 'Terracina', 'Cassino', 'Civitavecchia'
    ]
}

# Model Configurations
MODEL_CONFIGS = {
    'simple_rnn': {
        'model_type': 'RNN',
        'hidden_size': 64,
        'num_layers': 2,
        'dropout': 0.2,
        'learning_rate': 0.001,
        'epochs': 50,
        'batch_size': 32
    },
    
    'lstm': {
        'model_type': 'LSTM',
        'hidden_size': 64,
        'num_layers': 2,
        'dropout': 0.2,
        'learning_rate': 0.001,
        'epochs': 50,
        'batch_size': 32
    },
    
    'deep_lstm': {
        'model_type': 'LSTM',
        'hidden_size': 128,
        'num_layers': 3,
        'dropout': 0.2,
        'learning_rate': 0.0005,
        'epochs': 50,
        'batch_size': 32
    },
    
    'quick_demo': {
        'model_type': 'LSTM',
        'hidden_size': 32,
        'num_layers': 2,
        'dropout': 0.2,
        'learning_rate': 0.001,
        'epochs': 10,
        'batch_size': 16
    }
}

# Enhanced API Configuration
API_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': True,
    'model_path': 'lstm_electricity_model.pth',
    'enable_weather_integration': True,
    'weather_cache_duration': 3600,  # seconds (1 hour)
    'max_request_timeout': 20,  # seconds for auto-forecast
    'api_version': '2.0'
}

# Visualization Configuration
VIZ_CONFIG = {
    'figure_size': (15, 10),
    'dpi': 300,
    'style': 'seaborn-v0_8',
    'colors': {
        'electricity': 'blue',
        'temperature': 'red',
        'prediction': 'orange',
        'actual': 'blue',
        'weather_forecast': 'green'
    }
}

# Feature Engineering
FEATURE_CONFIG = {
    'normalize_load': True,
    'normalize_temp': True,
    'add_seasonal': True,
    'add_weekend': True,
    'add_day_of_year': True,
    'include_weather_context': True,
    'weather_features': [
        'temperature', 'humidity', 'precipitation', 'wind_speed'
    ]
}

# Seasons mapping for Italy
SEASONS = {
    'winter': [12, 1, 2],
    'spring': [3, 4, 5], 
    'summer': [6, 7, 8],
    'autumn': [9, 10, 11]
}

# Lazio Region Information
LAZIO_INFO = {
    'region_name': 'Lazio',
    'country': 'Italy',
    'capital': 'Roma',
    'timezone': 'Europe/Rome',
    'electricity_grid': 'Center-North Italy',
    'population': 5865544,  # 2024 estimate
    'area_km2': 17232,
    'provinces': [
        'Roma', 'Latina', 'Frosinone', 'Rieti', 'Viterbo'
    ],
    'major_cities': [
        {'name': 'Roma', 'coordinates': (41.9028, 12.4964), 'population': 2872800},
        {'name': 'Latina', 'coordinates': (41.4677, 12.9037), 'population': 125000},
        {'name': 'Frosinone', 'coordinates': (41.6359, 13.3511), 'population': 46000},
        {'name': 'Rieti', 'coordinates': (42.4014, 12.8623), 'population': 47700},
        {'name': 'Viterbo', 'coordinates': (42.4175, 12.1067), 'population': 67000}
    ]
}
