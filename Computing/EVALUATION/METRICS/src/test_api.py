#!/usr/bin/env python3
"""
Test script for the Electricity Forecasting API
This script tests various API endpoints and validates responses
"""

import requests
import json
import time
from datetime import datetime, timedelta

API_BASE_URL = "http://localhost:5000"

def test_api_endpoints():
    """
    Test all API endpoints
    """
    print("🧪 TESTING ELECTRICITY FORECASTING API")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("\n1. Testing server connectivity...")
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            print(f"   Response: {response.json()['service']}")
        else:
            print(f"❌ Server error: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("   Make sure to start the API server: python api_server.py")
        return False
    
    # Test 2: Check model status
    print("\n2. Testing model status endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/model/status")
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ Model status: {status_data['status']}")
            if status_data['status'] == 'available':
                print(f"   Model type: {status_data.get('model_type', 'Unknown')}")
            else:
                print(f"   Message: {status_data.get('message', 'No message')}")
        else:
            print(f"❌ Model status error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking model status: {e}")
    
    # Test 3: Get sample data format
    print("\n3. Testing sample data endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/data/sample")
        if response.status_code == 200:
            print("✅ Sample data format retrieved")
            sample_data = response.json()
            print(f"   Required fields: {sample_data['required_fields']}")
        else:
            print(f"❌ Sample data error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting sample data: {e}")
    
    # Test 4: Test forecasting with sample data
    print("\n4. Testing forecasting endpoint...")
    
    # Generate sample historical data
    sample_request = generate_sample_request()
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/forecast/next-day",
            json=sample_request,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            forecast_data = response.json()
            print("✅ Forecast successful!")
            print(f"   Predicted load: {forecast_data['forecast']['predicted_load_mw']} MW")
            print(f"   Forecast date: {forecast_data['forecast']['date']}")
            print(f"   Input temperature: {forecast_data['forecast']['input_temperature']}°C")
            print(f"   Confidence interval: {forecast_data['forecast']['confidence_interval']['lower']:.1f} - {forecast_data['forecast']['confidence_interval']['upper']:.1f} MW")
        else:
            print(f"❌ Forecast error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error message: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error making forecast request: {e}")
    
    # Test 5: Test error handling
    print("\n5. Testing error handling...")
    
    # Test with invalid data
    invalid_request = {"invalid": "data"}
    try:
        response = requests.post(
            f"{API_BASE_URL}/forecast/next-day",
            json=invalid_request,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 400:
            print("✅ Error handling works correctly")
            error_data = response.json()
            print(f"   Error message: {error_data.get('error', 'No error message')}")
        else:
            print(f"❌ Expected 400 error, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing error handling: {e}")
    
    # Test 6: Test non-existent endpoint
    print("\n6. Testing 404 handling...")
    try:
        response = requests.get(f"{API_BASE_URL}/nonexistent")
        if response.status_code == 404:
            print("✅ 404 handling works correctly")
        else:
            print(f"❌ Expected 404, got {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing 404: {e}")
    
    print("\n🎉 API testing completed!")
    return True

def generate_sample_request():
    """
    Generate sample request data for testing
    """
    # Generate 30 days of sample historical data
    base_date = datetime.now() - timedelta(days=30)
    historical_data = []
    
    for i in range(30):
        date = base_date + timedelta(days=i)
        
        # Simulate realistic electricity load (MW)
        # Base load with seasonal and random variation
        base_load = 15000
        seasonal_factor = 1 + 0.2 * (1 if date.month in [6, 7, 8, 12, 1, 2] else 0)  # Higher in summer/winter
        random_factor = 1 + (hash(str(date)) % 1000) / 10000  # Pseudo-random variation
        load = base_load * seasonal_factor * random_factor
        
        # Simulate temperature (Celsius)
        # Seasonal temperature variation
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
    
    # Next day temperature
    next_day_temp = 18.5
    
    return {
        "historical_data": historical_data,
        "next_day_temperature": next_day_temp
    }

def benchmark_api_performance():
    """
    Benchmark API response times
    """
    print("\n⏱️  BENCHMARKING API PERFORMANCE")
    print("=" * 40)
    
    sample_request = generate_sample_request()
    
    # Test multiple requests
    response_times = []
    num_requests = 5
    
    for i in range(num_requests):
        print(f"Request {i+1}/{num_requests}...", end=" ")
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{API_BASE_URL}/forecast/next-day",
                json=sample_request,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = end_time - start_time
                response_times.append(response_time)
                print(f"✅ {response_time:.3f}s")
            else:
                print(f"❌ Error {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        print(f"\n📊 Performance Results:")
        print(f"   • Average response time: {avg_time:.3f}s")
        print(f"   • Minimum response time: {min_time:.3f}s")
        print(f"   • Maximum response time: {max_time:.3f}s")
        print(f"   • Successful requests: {len(response_times)}/{num_requests}")

def test_curl_commands():
    """
    Generate and display curl commands for manual testing
    """
    print("\n📋 CURL COMMANDS FOR MANUAL TESTING")
    print("=" * 40)
    
    sample_request = generate_sample_request()
    
    print("\n1. Check server status:")
    print(f"curl {API_BASE_URL}/")
    
    print("\n2. Check model status:")
    print(f"curl {API_BASE_URL}/model/status")
    
    print("\n3. Get sample data format:")
    print(f"curl {API_BASE_URL}/data/sample")
    
    print("\n4. Make forecast request:")
    print(f"curl -X POST {API_BASE_URL}/forecast/next-day \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "historical_data": [')
    
    # Show first 3 entries for brevity
    for i, entry in enumerate(sample_request["historical_data"][:3]):
        comma = "," if i < 2 else ""
        print(f'      {{"date": "{entry["date"]}", "load": {entry["load"]}, "temperature": {entry["temperature"]}}}{comma}')
    
    print("    ],")
    print(f'    "next_day_temperature": {sample_request["next_day_temperature"]}')
    print("  }'")

def main():
    """
    Main test function
    """
    print("ELECTRICITY FORECASTING API TESTER")
    print("Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Run basic API tests
    if test_api_endpoints():
        # If basic tests pass, run performance benchmark
        benchmark_api_performance()
    
    # Show curl commands for manual testing
    test_curl_commands()

if __name__ == "__main__":
    main()
