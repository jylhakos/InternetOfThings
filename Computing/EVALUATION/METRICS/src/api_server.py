from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import torch
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import joblib
import os
from electricity_forecasting import ElectricityForecastModel
from weather_service import WeatherService, WeatherDataProcessor

app = Flask(__name__)
api = Api(app)

class ElectricityForecastAPI:
    """
    RESTful API for electricity consumption forecasting with real-time weather
    """
    
    def __init__(self):
        self.model = None
        self.model_path = 'lstm_electricity_model.pth'
        self.weather_service = WeatherService()
        self.weather_processor = WeatherDataProcessor()
        self.load_model()
    
    def load_model(self):
        """Load the trained model"""
        if os.path.exists(self.model_path):
            try:
                self.model = ElectricityForecastModel()
                self.model.load_model(self.model_path)
                print("Model loaded successfully!")
            except Exception as e:
                print(f"Error loading model: {e}")
                self.model = None
        else:
            print(f"Model file {self.model_path} not found!")
            self.model = None

class NextDayForecast(Resource):
    """
    API endpoint for next day electricity consumption forecast
    """
    
    def __init__(self):
        self.api_model = ElectricityForecastAPI()
    
    def post(self):
        """
        POST /forecast/next-day
        
        Expected JSON payload:
        {
            "historical_data": [
                {
                    "date": "2024-12-30",
                    "load": 15000.5,
                    "temperature": 12.5
                },
                ...
            ],
            "next_day_temperature": 13.2
        }
        """
        try:
            data = request.get_json()
            
            if not data:
                return {'error': 'No JSON data provided'}, 400
            
            # Validate required fields
            if 'historical_data' not in data:
                return {'error': 'historical_data is required'}, 400
            
            if 'next_day_temperature' not in data:
                return {'error': 'next_day_temperature is required'}, 400
            
            historical_data = data['historical_data']
            next_day_temp = data['next_day_temperature']
            
            # Validate historical data length
            if len(historical_data) < 24:
                return {'error': 'At least 24 days of historical data required'}, 400
            
            # Check if model is loaded
            if self.api_model.model is None:
                return {'error': 'Model not available. Please train the model first.'}, 500
            
            # Prepare input sequence
            sequence = self._prepare_sequence(historical_data[-24:], next_day_temp)
            
            # Make prediction
            prediction = self.api_model.model.predict_next_day(sequence)
            
            # Calculate confidence metrics
            historical_loads = [item['load'] for item in historical_data[-7:]]  # Last week
            recent_avg = np.mean(historical_loads)
            volatility = np.std(historical_loads)
            
            # Prepare response
            response = {
                'forecast': {
                    'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'predicted_load_mw': round(float(prediction), 2),
                    'confidence_interval': {
                        'lower': round(float(prediction - 1.96 * volatility), 2),
                        'upper': round(float(prediction + 1.96 * volatility), 2)
                    },
                    'model_type': self.api_model.model.model_type,
                    'input_temperature': next_day_temp
                },
                'context': {
                    'recent_average_load': round(recent_avg, 2),
                    'recent_volatility': round(volatility, 2),
                    'historical_days_used': len(historical_data)
                },
                'status': 'success'
            }
            
            return response, 200
            
        except Exception as e:
            return {'error': f'Prediction failed: {str(e)}'}, 500
    
    def _prepare_sequence(self, historical_data, next_day_temp):
        """
        Prepare input sequence for the model
        """
        # Extract features from historical data
        loads = [item['load'] for item in historical_data]
        temps = [item['temperature'] for item in historical_data]
        
        # Normalize using the model's scalers
        loads_normalized = self.api_model.model.load_scaler.transform(np.array(loads).reshape(-1, 1))
        temps_normalized = self.api_model.model.temp_scaler.transform(np.array(temps).reshape(-1, 1))
        
        # Add time-based features (simplified)
        # In a real implementation, you'd calculate actual day_of_year and season
        day_of_year_features = np.linspace(0, 1, len(historical_data)).reshape(-1, 1)
        
        # Simple season encoding (this should match your training data preparation)
        season_features = np.zeros((len(historical_data), 4))  # 4 seasons
        for i in range(len(historical_data)):
            season_features[i, 0] = 1  # Default to winter, you'd calculate this properly
        
        # Combine features
        sequence = np.concatenate([
            loads_normalized,
            temps_normalized,
            day_of_year_features,
            season_features
        ], axis=1)
        
        return torch.FloatTensor(sequence).unsqueeze(0)

class ModelStatus(Resource):
    """
    API endpoint to check model status
    """
    
    def __init__(self):
        self.api_model = ElectricityForecastAPI()
    
    def get(self):
        """
        GET /model/status
        """
        if self.api_model.model is None:
            return {
                'status': 'unavailable',
                'message': 'Model not loaded',
                'model_file': self.api_model.model_path,
                'file_exists': os.path.exists(self.api_model.model_path)
            }, 200
        
        return {
            'status': 'available',
            'message': 'Model ready for predictions',
            'model_type': self.api_model.model.model_type,
            'sequence_length': self.api_model.model.sequence_length,
            'hidden_size': self.api_model.model.hidden_size,
            'model_file': self.api_model.model_path
        }, 200

class AutoForecast(Resource):
    """
    API endpoint for automatic next-day forecast with real-time weather data
    """
    
    def __init__(self):
        self.api_model = ElectricityForecastAPI()
    
    def post(self):
        """
        POST /forecast/auto
        
        Expected JSON payload:
        {
            "historical_data": [
                {
                    "date": "2024-12-30",
                    "load": 15000.5,
                    "temperature": 12.5
                },
                ...
            ],
            "city": "Roma" (optional, defaults to Roma)
        }
        """
        try:
            data = request.get_json()
            
            if not data:
                return {'error': 'No JSON data provided'}, 400
            
            # Validate required fields
            if 'historical_data' not in data:
                return {'error': 'historical_data is required'}, 400
            
            historical_data = data['historical_data']
            city = data.get('city', 'Roma')  # Default to Roma, Lazio
            
            # Validate historical data length
            if len(historical_data) < 24:
                return {'error': 'At least 24 days of historical data required'}, 400
            
            # Check if model is loaded
            if self.api_model.model is None:
                return {'error': 'Model not available. Please train the model first.'}, 500
            
            # Get real-time weather forecast
            print(f"Getting tomorrow's weather for {city}, Lazio, Italy...")
            tomorrow_temp = self.api_model.weather_service.get_tomorrow_temperature(city)
            
            if tomorrow_temp is None:
                return {'error': 'Failed to fetch tomorrow\'s weather data. Please try again or use manual forecast endpoint.'}, 503
            
            # Prepare input sequence
            sequence = self._prepare_sequence(historical_data[-24:], tomorrow_temp)
            
            # Make prediction
            prediction = self.api_model.model.predict_next_day(sequence)
            
            # Calculate confidence metrics
            historical_loads = [item['load'] for item in historical_data[-7:]]  # Last week
            recent_avg = np.mean(historical_loads)
            volatility = np.std(historical_loads)
            
            # Get additional weather context
            weather_context = self._get_weather_context(city)
            
            # Prepare response
            response = {
                'forecast': {
                    'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'predicted_load_mw': round(float(prediction), 2),
                    'confidence_interval': {
                        'lower': round(float(prediction - 1.96 * volatility), 2),
                        'upper': round(float(prediction + 1.96 * volatility), 2)
                    },
                    'model_type': self.api_model.model.model_type,
                    'location': f"{city}, Lazio, Italy"
                },
                'weather': {
                    'tomorrow_temperature': tomorrow_temp,
                    'data_source': 'Open-Meteo API',
                    'forecast_region': 'Lazio, Italy',
                    'additional_context': weather_context
                },
                'context': {
                    'recent_average_load': round(recent_avg, 2),
                    'recent_volatility': round(volatility, 2),
                    'historical_days_used': len(historical_data),
                    'auto_weather_enabled': True
                },
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'api_version': '2.0',
                    'features': ['real_time_weather', 'geocoding', 'lstm_forecasting']
                },
                'status': 'success'
            }
            
            return response, 200
            
        except Exception as e:
            return {'error': f'Auto-forecast failed: {str(e)}'}, 500
    
    def _prepare_sequence(self, historical_data, next_day_temp):
        """
        Prepare input sequence for the model
        """
        # Extract features from historical data
        loads = [item['load'] for item in historical_data]
        temps = [item['temperature'] for item in historical_data]
        
        # Normalize using the model's scalers
        loads_normalized = self.api_model.model.load_scaler.transform(np.array(loads).reshape(-1, 1))
        temps_normalized = self.api_model.model.temp_scaler.transform(np.array(temps).reshape(-1, 1))
        
        # Add time-based features (simplified)
        # In a real implementation, you'd calculate actual day_of_year and season
        day_of_year_features = np.linspace(0, 1, len(historical_data)).reshape(-1, 1)
        
        # Simple season encoding (this should match your training data preparation)
        season_features = np.zeros((len(historical_data), 4))  # 4 seasons
        for i in range(len(historical_data)):
            season_features[i, 0] = 1  # Default to winter, you'd calculate this properly
        
        # Combine features
        sequence = np.concatenate([
            loads_normalized,
            temps_normalized,
            day_of_year_features,
            season_features
        ], axis=1)
        
        return torch.FloatTensor(sequence).unsqueeze(0)
    
    def _get_weather_context(self, city):
        """
        Get additional weather context for the forecast
        """
        try:
            # Get coordinates for the city
            coords = self.api_model.weather_service.get_coordinates(city, "Lazio", "Italy")
            if coords:
                # Get current weather
                current_weather = self.api_model.weather_service.get_current_weather(coords[0], coords[1])
                if current_weather and 'current_weather' in current_weather:
                    current = current_weather['current_weather']
                    return {
                        'current_temperature': current.get('temperature'),
                        'current_conditions': current.get('weathercode'),
                        'coordinates': f"{coords[0]:.4f}, {coords[1]:.4f}"
                    }
            return None
        except Exception:
            return None

class WeatherInfo(Resource):
    """
    API endpoint to get weather information for Lazio region
    """
    
    def __init__(self):
        self.weather_service = WeatherService()
    
    def get(self):
        """
        GET /weather/info?city=Roma
        """
        city = request.args.get('city', 'Roma')
        
        try:
            # Get tomorrow's temperature
            tomorrow_temp = self.weather_service.get_tomorrow_temperature(city)
            
            # Get coordinates
            coords = self.weather_service.get_coordinates(city, "Lazio", "Italy")
            
            # Get extended forecast
            extended_forecast = self.weather_service.get_extended_forecast(city, 7)
            
            response = {
                'location': {
                    'city': city,
                    'region': 'Lazio',
                    'country': 'Italy',
                    'coordinates': coords
                },
                'tomorrow_temperature': tomorrow_temp,
                'extended_forecast_available': extended_forecast is not None,
                'data_source': 'Open-Meteo API',
                'status': 'success' if tomorrow_temp is not None else 'partial'
            }
            
            if extended_forecast:
                daily_data = extended_forecast.get('daily', {})
                dates = daily_data.get('time', [])
                temps = daily_data.get('temperature_2m_mean', [])
                
                if dates and temps:
                    forecast_summary = []
                    for i, (date, temp) in enumerate(zip(dates[:7], temps[:7])):
                        forecast_summary.append({
                            'date': date,
                            'temperature': round(temp, 1) if temp else None
                        })
                    
                    response['weekly_forecast'] = forecast_summary
            
            return response, 200
            
        except Exception as e:
            return {'error': f'Weather information request failed: {str(e)}'}, 500
    """
    API endpoint to get sample historical data format
    """
    
    def get(self):
        """
        GET /data/sample
        """
        sample_data = {
            "description": "Sample format for historical data",
            "required_fields": {
                "historical_data": "Array of daily records (minimum 24 days)",
                "next_day_temperature": "Predicted temperature for the next day (°C)"
            },
            "sample_request": {
                "historical_data": [
                    {
                        "date": "2024-12-06",
                        "load": 14500.25,
                        "temperature": 8.5
                    },
                    {
                        "date": "2024-12-07",
                        "load": 15200.80,
                        "temperature": 6.2
                    }
                ],
                "next_day_temperature": 7.8
            },
            "notes": [
                "Load values should be in MW (Megawatts)",
                "Temperature values should be in Celsius",
                "At least 24 days of historical data required",
                "More historical data may improve prediction accuracy"
            ]
        }
        
        return sample_data, 200

class HistoricalData(Resource):
    """
    API endpoint to get sample historical data format
    """
    
    def get(self):
        """
        GET /data/sample
        """
        sample_data = {
            "description": "Sample format for historical data with automatic weather integration",
            "required_fields": {
                "historical_data": "Array of daily records (minimum 24 days)",
                "city": "City in Lazio for weather forecast (optional, defaults to Roma)"
            },
            "endpoints": {
                "manual_forecast": {
                    "url": "/forecast/next-day",
                    "description": "Manual forecast with provided temperature",
                    "requires": ["historical_data", "next_day_temperature"]
                },
                "auto_forecast": {
                    "url": "/forecast/auto", 
                    "description": "Automatic forecast with real-time weather from Open-Meteo",
                    "requires": ["historical_data"],
                    "optional": ["city"]
                }
            },
            "sample_manual_request": {
                "historical_data": [
                    {
                        "date": "2024-12-06",
                        "load": 14500.25,
                        "temperature": 8.5
                    },
                    {
                        "date": "2024-12-07",
                        "load": 15200.80,
                        "temperature": 6.2
                    }
                ],
                "next_day_temperature": 7.8
            },
            "sample_auto_request": {
                "historical_data": [
                    {
                        "date": "2024-12-06",
                        "load": 14500.25,
                        "temperature": 8.5
                    },
                    {
                        "date": "2024-12-07", 
                        "load": 15200.80,
                        "temperature": 6.2
                    }
                ],
                "city": "Roma"
            },
            "supported_cities": [
                "Roma", "Latina", "Frosinone", "Rieti", "Viterbo"
            ],
            "notes": [
                "Load values should be in MW (Megawatts)",
                "Temperature values should be in Celsius",
                "At least 24 days of historical data required",
                "Auto-forecast fetches real-time weather from Open-Meteo API",
                "Weather data covers Lazio region, Italy",
                "More historical data may improve prediction accuracy"
            ]
        }
        
        return sample_data, 200

# Register API endpoints
api.add_resource(NextDayForecast, '/forecast/next-day')
api.add_resource(AutoForecast, '/forecast/auto')
api.add_resource(ModelStatus, '/model/status')
api.add_resource(WeatherInfo, '/weather/info')
api.add_resource(HistoricalData, '/data/sample')

@app.route('/')
def home():
    """
    Home endpoint with API documentation
    """
    documentation = {
        "service": "Electricity Consumption Forecasting API with Real-Time Weather",
        "description": "RESTful API for predicting next-day electricity consumption using RNN/LSTM models with automatic weather integration",
        "version": "2.0.0",
        "region": "Lazio, Italy",
        "weather_provider": "Open-Meteo API",
        "endpoints": {
            "GET /": "This documentation",
            "GET /model/status": "Check model availability and status",
            "GET /data/sample": "Get sample data format and usage examples",
            "GET /weather/info": "Get weather information for Lazio region",
            "POST /forecast/next-day": "Manual forecast with provided temperature",
            "POST /forecast/auto": "Automatic forecast with real-time weather (NEW)"
        },
        "new_features": {
            "automatic_weather": "Fetches tomorrow's temperature automatically using Open-Meteo API",
            "geocoding": "Converts city names to coordinates for accurate weather data",
            "lazio_region_focus": "Optimized for Lazio region cities in Italy",
            "extended_weather": "Provides additional weather context and weekly forecasts"
        },
        "usage_examples": {
            "auto_forecast_curl": """curl -X POST http://localhost:5000/forecast/auto \\
  -H "Content-Type: application/json" \\
  -d '{
    "historical_data": [
      {"date": "2024-12-06", "load": 14500.25, "temperature": 8.5},
      {"date": "2024-12-07", "load": 15200.80, "temperature": 6.2}
    ],
    "city": "Roma"
  }'""",
            "weather_info_curl": """curl "http://localhost:5000/weather/info?city=Roma\"""",
            "manual_forecast_curl": """curl -X POST http://localhost:5000/forecast/next-day \\
  -H "Content-Type: application/json" \\
  -d '{
    "historical_data": [
      {"date": "2024-12-06", "load": 14500.25, "temperature": 8.5}
    ],
    "next_day_temperature": 7.8
  }'"""
        },
        "supported_cities": [
            "Roma (default)", "Latina", "Frosinone", "Rieti", "Viterbo"
        ],
        "model_info": {
            "algorithm": "RNN/LSTM with PyTorch",
            "features": ["Historical electricity load", "Real-time temperature", "Seasonal patterns", "Geographic location"],
            "output": "Next day electricity consumption in MW for Lazio region",
            "weather_integration": "Open-Meteo API with geocoding support"
        }
    }
    
    return jsonify(documentation)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting Electricity Forecasting API with Real-Time Weather...")
    print("=" * 60)
    print("🌍 Region: Lazio, Italy")
    print("🌡️  Weather Provider: Open-Meteo API")
    print("🤖 Model: RNN/LSTM with PyTorch")
    print("=" * 60)
    print("Available endpoints:")
    print("  GET  /                      - API documentation")
    print("  GET  /model/status          - Model status")
    print("  GET  /data/sample           - Sample data format")
    print("  GET  /weather/info          - Weather information")
    print("  POST /forecast/next-day     - Manual forecast")
    print("  POST /forecast/auto         - Auto forecast with real-time weather")
    print("\n🚀 NEW: Automatic Weather Integration!")
    print("Example auto-forecast cURL command:")
    print("""curl -X POST http://localhost:5000/forecast/auto \\
  -H "Content-Type: application/json" \\
  -d '{
    "historical_data": [
      {"date": "2024-12-06", "load": 14500, "temperature": 8.5}
    ],
    "city": "Roma"
  }'""")
    print("\n🌡️  Get weather info:")
    print('curl "http://localhost:5000/weather/info?city=Roma"')
    
    app.run(debug=True, host='0.0.0.0', port=5000)
