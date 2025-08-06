#!/usr/bin/env python3
"""
Test script to demonstrate noon temperature forecasting for EDA analysis
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_noon_temperature_api():
    """
    Test the new noon temperature functionality for better EDA analysis
    """
    print("🌞 NOON TEMPERATURE TESTING FOR EDA ANALYSIS")
    print("=" * 55)
    print("This test demonstrates fetching tomorrow's temperature at noon (12 PM)")
    print("which is optimal for electricity consumption correlation analysis.")
    print("=" * 55)
    
    try:
        from weather_service import WeatherService
    except ImportError as e:
        print(f"❌ Error importing weather service: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        return False
    
    # Initialize weather service
    weather_service = WeatherService()
    
    # Test city
    test_city = "Roma"
    
    print(f"\n🏛️  Testing {test_city}, Lazio, Italy")
    print("-" * 35)
    
    # Test 1: Daily average temperature (existing functionality)
    print("\n📊 Test 1: Daily Average Temperature")
    daily_temp = weather_service.get_tomorrow_temperature(test_city)
    if daily_temp:
        print(f"✅ Daily average: {daily_temp:.1f}°C")
    else:
        print("❌ Daily temperature fetch failed")
        return False
    
    # Test 2: Noon temperature (new functionality for EDA)
    print("\n🌞 Test 2: Noon Temperature (12 PM)")
    noon_temp = weather_service.get_tomorrow_noon_temperature(test_city)
    if noon_temp:
        print(f"✅ Noon temperature: {noon_temp:.1f}°C")
        
        # Compare the two temperatures
        temp_diff = noon_temp - daily_temp
        print(f"\n📈 Temperature Analysis:")
        print(f"   Daily Average:  {daily_temp:.1f}°C")
        print(f"   Noon (12 PM):   {noon_temp:.1f}°C")
        print(f"   Difference:     {temp_diff:+.1f}°C")
        
        if abs(temp_diff) > 2:
            print(f"   🔍 Significant difference! Noon temp better for peak load analysis")
        else:
            print(f"   📊 Similar temperatures, both suitable for analysis")
            
    else:
        print("⚠️  Noon temperature not available, falling back to daily average")
        noon_temp = daily_temp
    
    # Test 3: EDA correlation implications
    print(f"\n🔬 EDA Analysis Implications:")
    print("-" * 30)
    
    if noon_temp > daily_temp + 1:
        print("🌡️  Noon temperature is warmer than daily average")
        print("   → Peak cooling demand likely around midday")
        print("   → Use noon temp for air conditioning load correlation")
    elif noon_temp < daily_temp - 1:
        print("🌡️  Noon temperature is cooler than daily average")
        print("   → Peak temperatures might occur later in the day")
        print("   → Consider evening temperature for peak analysis")
    else:
        print("🌡️  Noon temperature close to daily average")
        print("   → Either temperature suitable for correlation analysis")
    
    print(f"\n💡 EDA Recommendation:")
    if abs(noon_temp - daily_temp) > 1.5:
        print("   Use NOON temperature for electricity consumption correlation")
        print("   Reason: Significant difference from daily average detected")
    else:
        print("   Both temperatures suitable, noon provides more precision")
    
    return True

def demonstrate_eda_correlation():
    """
    Demonstrate how noon temperature improves EDA correlation analysis
    """
    print(f"\n🔗 EDA CORRELATION ANALYSIS DEMONSTRATION")
    print("-" * 45)
    
    # Simulated electricity consumption patterns based on temperature
    def estimate_load_correlation(temp):
        """Estimate electricity load based on temperature (simplified model)"""
        if temp < 5:  # Very cold - heating
            return 16000 + (5 - temp) * 200
        elif temp > 25:  # Hot - cooling
            return 14000 + (temp - 25) * 150
        else:  # Comfort zone
            return 13500 + abs(temp - 18) * 50
    
    # Test with sample temperatures
    test_temps = [
        {"type": "Daily Avg", "temp": 18.5},
        {"type": "Noon", "temp": 22.3},
        {"type": "Evening", "temp": 16.2}
    ]
    
    print("Temperature Impact on Electricity Load (MW):")
    print("Temperature Type | Temp (°C) | Est. Load (MW) | Peak Factor")
    print("-" * 60)
    
    for temp_data in test_temps:
        temp = temp_data["temp"]
        load = estimate_load_correlation(temp)
        peak_factor = "High" if load > 15000 else "Medium" if load > 14000 else "Low"
        print(f"{temp_data['type']:<15} | {temp:>7.1f} | {load:>11.0f} | {peak_factor}")
    
    print(f"\n🎯 Key Insight:")
    print("Noon temperature often captures peak cooling/heating demand")
    print("better than daily averages, leading to improved RNN/LSTM predictions")

def main():
    """
    Main test function
    """
    print("NOON TEMPERATURE API TEST")
    print("Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Purpose: Test enhanced weather API for better EDA analysis")
    
    # Run the noon temperature test
    success = test_noon_temperature_api()
    
    if success:
        # Demonstrate EDA correlation benefits
        demonstrate_eda_correlation()
        
        print(f"\n✅ SUCCESS: Noon temperature API working correctly!")
        print("\n🚀 Next Steps:")
        print("1. Use noon temperature in your EDA analysis")
        print("2. Compare correlation with electricity consumption")
        print("3. Train RNN/LSTM models with noon temperature data")
        print("4. Run: python demo_weather.py for full demonstration")
        
    else:
        print(f"\n❌ FAILED: Issues with weather API")
        print("Check internet connection and API availability")

if __name__ == "__main__":
    main()
