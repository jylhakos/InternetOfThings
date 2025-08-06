#!/usr/bin/env python3
"""
Weather Integration Demo
Demonstrates the new weather API integration features
"""

import sys
import os
import time
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_weather_integration():
    """
    Demonstrate weather integration capabilities
    """
    print("🌡️  WEATHER INTEGRATION DEMO")
    print("=" * 40)
    print("Region: Lazio, Italy")
    print("Weather Provider: Open-Meteo API")
    print("Geocoding: OpenStreetMap Nominatim")
    print("=" * 40)
    
    try:
        from weather_service import WeatherService, WeatherDataProcessor
    except ImportError as e:
        print(f"❌ Error importing weather service: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        return False
    
    # Initialize weather service
    weather_service = WeatherService()
    processor = WeatherDataProcessor()
    
    # Test cities in Lazio
    lazio_cities = ['Roma', 'Latina', 'Frosinone', 'Rieti', 'Viterbo']
    
    print(f"\n🏛️  Testing Lazio Cities")
    print("-" * 30)
    
    results = {}
    
    for city in lazio_cities:
        print(f"\n📍 {city}:")
        
        # Get coordinates
        coords = weather_service.get_coordinates(city, "Lazio", "Italy")
        if coords:
            print(f"   Coordinates: {coords[0]:.4f}, {coords[1]:.4f}")
            results[city] = {'coordinates': coords}
        else:
            print(f"   ❌ Geocoding failed")
            continue
        
        # Get tomorrow's temperature
        tomorrow_temp = weather_service.get_tomorrow_temperature(city)
        if tomorrow_temp:
            print(f"   Tomorrow's temp (avg): {tomorrow_temp:.1f}°C")
            results[city]['temperature'] = tomorrow_temp
        else:
            print(f"   ❌ Weather forecast failed")
            continue
        
        # Get tomorrow's noon temperature for better EDA analysis
        noon_temp = weather_service.get_tomorrow_noon_temperature(city)
        if noon_temp:
            print(f"   Tomorrow's noon temp: {noon_temp:.1f}°C")
            results[city]['noon_temperature'] = noon_temp
        else:
            print(f"   ⚠️  Noon temperature not available")
    
    # Summary
    print(f"\n📊 SUMMARY")
    print("-" * 20)
    successful_cities = len([city for city, data in results.items() if 'temperature' in data])
    noon_cities = len([city for city, data in results.items() if 'noon_temperature' in data])
    print(f"Cities processed: {len(lazio_cities)}")
    print(f"Successful forecasts: {successful_cities}")
    print(f"Noon temperatures: {noon_cities}")
    print(f"Success rate: {(successful_cities/len(lazio_cities)*100):.1f}%")
    
    # Show temperature ranges
    if successful_cities > 0:
        temperatures = [data['temperature'] for data in results.values() if 'temperature' in data]
        print(f"Avg temperature range: {min(temperatures):.1f}°C - {max(temperatures):.1f}°C")
        
        if noon_cities > 0:
            noon_temperatures = [data['noon_temperature'] for data in results.values() if 'noon_temperature' in data]
            print(f"Noon temperature range: {min(noon_temperatures):.1f}°C - {max(noon_temperatures):.1f}°C")
            avg_diff = sum(abs(results[city].get('noon_temperature', 0) - results[city].get('temperature', 0)) 
                          for city in results if 'noon_temperature' in results[city] and 'temperature' in results[city]) / noon_cities
            print(f"Avg difference (noon vs daily): {avg_diff:.1f}°C")
    
    return successful_cities > 0

def demo_forecast_integration():
    """
    Demonstrate forecast integration with weather data
    """
    print(f"\n🔮 FORECAST INTEGRATION DEMO")
    print("-" * 35)
    
    try:
        from weather_service import WeatherDataProcessor
    except ImportError:
        print("❌ Weather service not available")
        return False
    
    # Sample historical data for Lazio region
    sample_historical = [
        {"date": "2024-12-20", "load": 14200, "temperature": 9.5},
        {"date": "2024-12-21", "load": 14800, "temperature": 8.2},
        {"date": "2024-12-22", "load": 15100, "temperature": 7.1},
        {"date": "2024-12-23", "load": 15300, "temperature": 6.8},
        {"date": "2024-12-24", "load": 14900, "temperature": 8.0},
        {"date": "2024-12-25", "load": 14500, "temperature": 9.2},
        {"date": "2024-12-26", "load": 15200, "temperature": 7.5},
        {"date": "2024-12-27", "load": 14800, "temperature": 8.8},
        {"date": "2024-12-28", "load": 15400, "temperature": 6.5},
        {"date": "2024-12-29", "load": 15100, "temperature": 7.9},
    ]
    
    processor = WeatherDataProcessor()
    
    # Test forecast preparation for Roma
    print("Preparing forecast input for Roma (with noon temperature)...")
    forecast_input = processor.prepare_forecast_input(sample_historical, "Roma", use_noon_temp=True)
    
    if forecast_input:
        print("✅ Forecast input prepared successfully!")
        print(f"   Historical records: {len(forecast_input['historical_data'])}")
        print(f"   Next day temperature: {forecast_input['next_day_temperature']:.1f}°C")
        print(f"   Temperature type: {forecast_input['temperature_type']}")
        print(f"   Weather source: {forecast_input['weather_source']}")
        print(f"   Forecast date: {forecast_input['forecast_date']}")
        
        # Calculate temperature trend
        historical_temps = [item['temperature'] for item in sample_historical[-5:]]
        avg_recent_temp = sum(historical_temps) / len(historical_temps)
        temp_change = forecast_input['next_day_temperature'] - avg_recent_temp
        
        print(f"   Recent avg temp: {avg_recent_temp:.1f}°C")
        print(f"   Temperature change: {temp_change:+.1f}°C")
        
        # Test daily average for comparison
        print("\n📊 Testing daily average for comparison...")
        forecast_input_daily = processor.prepare_forecast_input(sample_historical, "Roma", use_noon_temp=False)
        if forecast_input_daily:
            temp_diff = forecast_input['next_day_temperature'] - forecast_input_daily['next_day_temperature']
            print(f"   Daily avg temperature: {forecast_input_daily['next_day_temperature']:.1f}°C")
            print(f"   Difference (noon vs daily): {temp_diff:+.1f}°C")
        
        return True
    else:
        print("❌ Forecast input preparation failed")
        return False

def show_api_examples():
    """
    Show practical API usage examples
    """
    print(f"\n📡 API USAGE EXAMPLES")
    print("-" * 25)
    
    print("\n1. Get weather info for Roma:")
    print('curl "http://localhost:5000/weather/info?city=Roma"')
    
    print("\n2. Auto-forecast with real-time weather:")
    print("""curl -X POST http://localhost:5000/forecast/auto \\
  -H "Content-Type: application/json" \\
  -d '{
    "historical_data": [
      {"date": "2024-12-29", "load": 15100, "temperature": 7.9}
    ],
    "city": "Roma"
  }'""")
    
    print("\n3. Test different Lazio cities:")
    cities = ['Roma', 'Latina', 'Frosinone']
    for city in cities:
        print(f'curl "http://localhost:5000/weather/info?city={city}"')

def performance_info():
    """
    Show performance and technical information
    """
    print(f"\n⚡ PERFORMANCE INFO")
    print("-" * 20)
    
    print("\nWeather API Performance:")
    print("• Geocoding: ~1-2 seconds per city")
    print("• Daily weather forecast: ~2-3 seconds per request")
    print("• Hourly weather forecast (noon): ~3-4 seconds per request")
    print("• Total auto-forecast: ~5-8 seconds")
    print("• Caching: Coordinates cached to improve speed")
    
    print("\nTemperature Options for EDA:")
    print("• Daily Average: Mean temperature for the entire day")
    print("• Noon Temperature: Specific temperature at 12:00 PM")
    print("• Noon temperature is better for EDA correlation analysis")
    print("• Peak electricity consumption often correlates with noon temperature")
    
    print("\nAPI Rate Limits:")
    print("• Open-Meteo: 10,000 requests/day (free tier)")
    print("• Nominatim: 1 request/second")
    print("• Built-in rate limiting and error handling")
    
    print("\nReliability Features:")
    print("• Fallback from noon to daily average if hourly data unavailable")
    print("• Fallback to default coordinates")
    print("• Temperature estimation from historical data")
    print("• Graceful degradation on API failures")

def main():
    """
    Main demo function
    """
    print("ELECTRICITY FORECASTING - WEATHER INTEGRATION DEMO")
    print("Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Run weather integration demo
    weather_success = demo_weather_integration()
    
    # Run forecast integration demo
    forecast_success = demo_forecast_integration()
    
    # Show usage examples
    show_api_examples()
    
    # Show performance info
    performance_info()
    
    # Final summary
    print(f"\n🎯 DEMO SUMMARY")
    print("-" * 15)
    
    if weather_success and forecast_success:
        print("✅ Weather integration working correctly!")
        print("✅ Forecast integration successful!")
        print("\n🚀 Ready to use:")
        print("• Start API server: python api_server.py")
        print("• Test weather APIs: python test_weather_api.py")
        print("• Train models: python train_models.py")
    elif weather_success:
        print("✅ Weather integration working correctly!")
        print("⚠️  Forecast integration has issues")
        print("Check dependencies and model availability")
    else:
        print("❌ Weather integration issues detected")
        print("Please check:")
        print("• Internet connection")
        print("• Installed dependencies (pip install -r requirements.txt)")
        print("• API rate limits")

if __name__ == "__main__":
    main()
