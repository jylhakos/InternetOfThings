#!/usr/bin/env python3
"""
Enhanced test script for the Electricity Forecasting API with Weather Integration
Tests both manual and automatic forecasting endpoints
"""

import requests
import json
import time
from datetime import datetime, timedelta

API_BASE_URL = "http://localhost:5000"

def test_weather_integration():
    """
    Test the new weather integration features
    """
    print("🌡️  TESTING WEATHER INTEGRATION FEATURES")
    print("=" * 55)
    
    # Test 1: Weather info endpoint
    print("\n1. Testing weather information endpoint...")
    cities_to_test = ['Roma', 'Latina', 'Frosinone']
    
    for city in cities_to_test:
        try:
            response = requests.get(f"{API_BASE_URL}/weather/info", params={'city': city}, timeout=10)
            if response.status_code == 200:
                weather_data = response.json()
                print(f"✅ {city} weather info:")
                print(f"   Tomorrow's temp: {weather_data.get('tomorrow_temperature')}°C")
                print(f"   Coordinates: {weather_data.get('location', {}).get('coordinates')}")
                if 'weekly_forecast' in weather_data:
                    print(f"   Weekly forecast: {len(weather_data['weekly_forecast'])} days")
            else:
                print(f"❌ {city} weather info failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting weather for {city}: {e}")
    
    # Test 2: Auto-forecast endpoint
    print("\n2. Testing automatic forecast with real-time weather...")
    sample_request = generate_sample_historical_data()
    
    for city in ['Roma', 'Latina']:
        try:
            auto_request = {
                "historical_data": sample_request["historical_data"],
                "city": city
            }
            
            print(f"\nTesting auto-forecast for {city}...")
            response = requests.post(
                f"{API_BASE_URL}/forecast/auto",
                json=auto_request,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            if response.status_code == 200:
                forecast_data = response.json()
                print(f"✅ Auto-forecast successful for {city}!")
                print(f"   Predicted load: {forecast_data['forecast']['predicted_load_mw']} MW")
                print(f"   Weather temp: {forecast_data['weather']['tomorrow_temperature']}°C")
                print(f"   Location: {forecast_data['forecast']['location']}")
                print(f"   Weather source: {forecast_data['weather']['data_source']}")
            else:
                print(f"❌ Auto-forecast failed for {city}: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error')}")
                except:
                    print(f"   Response: {response.text}")
                    
        except Exception as e:
            print(f"❌ Error with auto-forecast for {city}: {e}")

def test_api_comparison():
    """
    Compare manual vs automatic forecasting
    """
    print("\n🔄 COMPARING MANUAL VS AUTOMATIC FORECASTING")
    print("=" * 50)
    
    sample_data = generate_sample_historical_data()
    
    # Test manual forecast first
    print("\n1. Manual forecast (user provides temperature)...")
    try:
        manual_request = {
            "historical_data": sample_data["historical_data"],
            "next_day_temperature": 12.5  # User-provided temperature
        }
        
        response = requests.post(
            f"{API_BASE_URL}/forecast/next-day",
            json=manual_request,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            manual_result = response.json()
            print("✅ Manual forecast successful!")
            print(f"   Predicted load: {manual_result['forecast']['predicted_load_mw']} MW")
            print(f"   Input temperature: {manual_result['forecast']['input_temperature']}°C")
        else:
            print(f"❌ Manual forecast failed: {response.status_code}")
            manual_result = None
            
    except Exception as e:
        print(f"❌ Manual forecast error: {e}")
        manual_result = None
    
    # Test automatic forecast
    print("\n2. Automatic forecast (real-time weather)...")
    try:
        auto_request = {
            "historical_data": sample_data["historical_data"],
            "city": "Roma"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/forecast/auto",
            json=auto_request,
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        if response.status_code == 200:
            auto_result = response.json()
            print("✅ Automatic forecast successful!")
            print(f"   Predicted load: {auto_result['forecast']['predicted_load_mw']} MW")
            print(f"   Real-time temperature: {auto_result['weather']['tomorrow_temperature']}°C")
            print(f"   Weather source: {auto_result['weather']['data_source']}")
        else:
            print(f"❌ Automatic forecast failed: {response.status_code}")
            auto_result = None
            
    except Exception as e:
        print(f"❌ Automatic forecast error: {e}")
        auto_result = None
    
    # Compare results
    if manual_result and auto_result:
        print("\n📊 COMPARISON RESULTS:")
        manual_load = manual_result['forecast']['predicted_load_mw']
        auto_load = auto_result['forecast']['predicted_load_mw']
        manual_temp = manual_result['forecast']['input_temperature']
        auto_temp = auto_result['weather']['tomorrow_temperature']
        
        print(f"   Manual forecast:    {manual_load} MW (temp: {manual_temp}°C)")
        print(f"   Automatic forecast: {auto_load} MW (temp: {auto_temp}°C)")
        print(f"   Load difference:    {auto_load - manual_load:+.1f} MW")
        print(f"   Temp difference:    {auto_temp - manual_temp:+.1f}°C")

def test_error_handling():
    """
    Test error handling for weather integration
    """
    print("\n⚠️  TESTING ERROR HANDLING")
    print("=" * 30)
    
    # Test 1: Invalid city
    print("\n1. Testing invalid city...")
    try:
        response = requests.get(f"{API_BASE_URL}/weather/info", params={'city': 'InvalidCity'})
        if response.status_code == 200:
            weather_data = response.json()
            if weather_data.get('tomorrow_temperature') is None:
                print("✅ Invalid city handled gracefully")
            else:
                print("⚠️  Invalid city returned data (might be valid)")
        else:
            print(f"✅ Invalid city returned error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing invalid city: {e}")
    
    # Test 2: Auto-forecast without internet (simulate)
    print("\n2. Testing auto-forecast error handling...")
    try:
        # Test with minimal data that might cause issues
        minimal_request = {
            "historical_data": [
                {"date": "2024-12-30", "load": 15000, "temperature": 10}
            ],  # Only 1 day instead of required 24
            "city": "Roma"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/forecast/auto",
            json=minimal_request,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        if response.status_code == 400:
            error_data = response.json()
            print("✅ Insufficient data error handled correctly")
            print(f"   Error message: {error_data.get('error')}")
        else:
            print(f"⚠️  Expected 400 error, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing auto-forecast error handling: {e}")

def benchmark_weather_performance():
    """
    Benchmark performance of weather-integrated endpoints
    """
    print("\n⏱️  BENCHMARKING WEATHER PERFORMANCE")
    print("=" * 40)
    
    sample_request = generate_sample_historical_data()
    
    # Benchmark weather info endpoint
    print("\n1. Weather info endpoint performance...")
    weather_times = []
    
    for i in range(3):
        start_time = time.time()
        try:
            response = requests.get(f"{API_BASE_URL}/weather/info", params={'city': 'Roma'}, timeout=10)
            end_time = time.time()
            
            if response.status_code == 200:
                weather_times.append(end_time - start_time)
                print(f"   Request {i+1}: {end_time - start_time:.2f}s")
            else:
                print(f"   Request {i+1}: Failed ({response.status_code})")
                
        except Exception as e:
            print(f"   Request {i+1}: Error ({e})")
    
    if weather_times:
        avg_weather_time = sum(weather_times) / len(weather_times)
        print(f"   Average weather API time: {avg_weather_time:.2f}s")
    
    # Benchmark auto-forecast endpoint
    print("\n2. Auto-forecast endpoint performance...")
    auto_forecast_times = []
    
    auto_request = {
        "historical_data": sample_request["historical_data"],
        "city": "Roma"
    }
    
    for i in range(2):  # Fewer iterations due to longer processing time
        start_time = time.time()
        try:
            response = requests.post(
                f"{API_BASE_URL}/forecast/auto",
                json=auto_request,
                headers={'Content-Type': 'application/json'},
                timeout=20
            )
            end_time = time.time()
            
            if response.status_code == 200:
                auto_forecast_times.append(end_time - start_time)
                print(f"   Request {i+1}: {end_time - start_time:.2f}s")
            else:
                print(f"   Request {i+1}: Failed ({response.status_code})")
                
        except Exception as e:
            print(f"   Request {i+1}: Error ({e})")
    
    if auto_forecast_times:
        avg_auto_time = sum(auto_forecast_times) / len(auto_forecast_times)
        print(f"   Average auto-forecast time: {avg_auto_time:.2f}s")

def generate_sample_historical_data():
    """
    Generate sample historical data for testing
    """
    base_date = datetime.now() - timedelta(days=30)
    historical_data = []
    
    for i in range(30):
        date = base_date + timedelta(days=i)
        
        # Simulate realistic electricity load for Lazio region
        base_load = 15000  # MW baseline for Lazio
        seasonal_factor = 1 + 0.15 * (1 if date.month in [6, 7, 8, 12, 1, 2] else 0)
        random_factor = 1 + (hash(str(date)) % 1000) / 10000
        load = base_load * seasonal_factor * random_factor
        
        # Simulate temperature for Roma/Lazio
        if date.month in [12, 1, 2]:  # Winter
            temp = 5 + (hash(str(date)) % 10)
        elif date.month in [6, 7, 8]:  # Summer
            temp = 25 + (hash(str(date)) % 10)
        else:  # Spring/Autumn
            temp = 15 + (hash(str(date)) % 10)
        
        historical_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "load": round(load, 2),
            "temperature": round(temp, 1)
        })
    
    return {"historical_data": historical_data}

def show_enhanced_curl_examples():
    """
    Show enhanced cURL examples for the new endpoints
    """
    print("\n📋 ENHANCED CURL EXAMPLES")
    print("=" * 30)
    
    sample_data = generate_sample_historical_data()
    
    print("\n1. Weather Information:")
    print('curl "http://localhost:5000/weather/info?city=Roma"')
    print('curl "http://localhost:5000/weather/info?city=Latina"')
    
    print("\n2. Automatic Forecast (Real-time Weather):")
    print("curl -X POST http://localhost:5000/forecast/auto \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "historical_data": [')
    
    # Show first 3 entries
    for i, entry in enumerate(sample_data["historical_data"][:3]):
        comma = "," if i < 2 else ""
        print(f'      {{"date": "{entry["date"]}", "load": {entry["load"]}, "temperature": {entry["temperature"]}}}{comma}')
    
    print("    ],")
    print('    "city": "Roma"')
    print("  }'")
    
    print("\n3. Manual Forecast (Traditional):")
    print("curl -X POST http://localhost:5000/forecast/next-day \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "historical_data": [')
    print(f'      {{"date": "{sample_data["historical_data"][0]["date"]}", "load": {sample_data["historical_data"][0]["load"]}, "temperature": {sample_data["historical_data"][0]["temperature"]}}}')
    print("    ],")
    print('    "next_day_temperature": 18.5')
    print("  }'")

def main():
    """
    Main test function for enhanced weather integration
    """
    print("ENHANCED ELECTRICITY FORECASTING API TESTER")
    print("Weather Integration & Real-time Forecasting")
    print("Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Region: Lazio, Italy")
    
    # Check server connectivity first
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print(f"\n❌ Server not responding: {response.status_code}")
            print("Make sure to start the API server: python api_server.py")
            return
    except requests.exceptions.RequestException:
        print(f"\n❌ Cannot connect to server at {API_BASE_URL}")
        print("Make sure to start the API server: python api_server.py")
        return
    
    print("\n✅ Server is running!")
    
    # Run enhanced tests
    test_weather_integration()
    test_api_comparison()
    test_error_handling()
    benchmark_weather_performance()
    show_enhanced_curl_examples()
    
    print("\n🎉 ENHANCED TESTING COMPLETED!")
    print("=" * 40)
    print("New features tested:")
    print("✅ Real-time weather integration")
    print("✅ Geocoding for Lazio cities")
    print("✅ Automatic vs manual forecasting")
    print("✅ Error handling improvements")
    print("✅ Performance benchmarking")

if __name__ == "__main__":
    main()
