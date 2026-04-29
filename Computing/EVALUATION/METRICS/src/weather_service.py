"""
Weather Service Module for Real-time Temperature Data
Handles geocoding and weather API calls for electricity forecasting
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time

class WeatherService:
    """
    Service class for fetching real-time weather data using Open-Meteo API
    """
    
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.geocoder = Nominatim(user_agent="electricity_forecasting_app")
        
        # Cache for coordinates to avoid repeated geocoding
        self.coordinates_cache = {}
        
        # Default location for Lazio, Italy
        self.default_location = {
            'city': 'Roma',
            'region': 'Lazio',
            'country': 'Italy'
        }
    
    def get_coordinates(self, city: str, region: str = "Lazio", country: str = "Italy") -> Optional[Tuple[float, float]]:
        """
        Get latitude and longitude coordinates for a given location using geocoding
        
        Args:
            city: City name (e.g., "Roma")
            region: Region/state name (e.g., "Lazio") 
            country: Country name (e.g., "Italy")
            
        Returns:
            Tuple of (latitude, longitude) or None if geocoding fails
        """
        # Create cache key
        location_key = f"{city}, {region}, {country}"
        
        # Check cache first
        if location_key in self.coordinates_cache:
            print(f"Using cached coordinates for {location_key}")
            return self.coordinates_cache[location_key]
        
        try:
            print(f"Geocoding location: {location_key}")
            
            # Try with full address first
            location = self.geocoder.geocode(location_key, timeout=10)
            
            if location is None:
                # Try with just city and country
                fallback_key = f"{city}, {country}"
                print(f"Trying fallback geocoding: {fallback_key}")
                location = self.geocoder.geocode(fallback_key, timeout=10)
            
            if location is None:
                # Try with just region and country
                region_key = f"{region}, {country}"
                print(f"Trying region geocoding: {region_key}")
                location = self.geocoder.geocode(region_key, timeout=10)
            
            if location:
                coordinates = (location.latitude, location.longitude)
                self.coordinates_cache[location_key] = coordinates
                
                print(f"✅ Geocoding successful:")
                print(f"   Location: {location.address}")
                print(f"   Coordinates: {coordinates[0]:.4f}, {coordinates[1]:.4f}")
                
                return coordinates
            else:
                print(f"❌ Geocoding failed for {location_key}")
                return None
                
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            print(f"❌ Geocoding error: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected geocoding error: {e}")
            return None
    
    def get_default_coordinates(self) -> Tuple[float, float]:
        """
        Get default coordinates for Lazio, Italy (Roma)
        
        Returns:
            Tuple of (latitude, longitude) for Roma, Lazio
        """
        # Roma, Lazio coordinates (approximate center)
        roma_coordinates = (41.9028, 12.4964)
        
        print(f"Using default coordinates for Roma, Lazio: {roma_coordinates}")
        return roma_coordinates
    
    def fetch_weather_forecast(self, latitude: float, longitude: float, days: int = 7, include_hourly: bool = False) -> Optional[Dict]:
        """
        Fetch weather forecast data from Open-Meteo API
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate  
            days: Number of forecast days (default 7)
            include_hourly: Whether to include hourly data for specific times (default False)
            
        Returns:
            Weather data dictionary or None if request fails
        """
        try:
            print(f"Fetching weather forecast for coordinates: {latitude:.4f}, {longitude:.4f}")
            
            # Prepare API parameters
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'daily': 'temperature_2m_max,temperature_2m_min,temperature_2m_mean',
                'timezone': 'Europe/Rome',
                'forecast_days': min(days, 16)  # Open-Meteo supports up to 16 days
            }
            
            # Add hourly data for more precise temperature at specific times (e.g., noon)
            if include_hourly:
                params['hourly'] = 'temperature_2m'
                params['forecast_hours'] = min(days * 24, 384)  # Up to 16 days hourly
                print("   Including hourly temperature data for noon analysis")
            
            # Make API request
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            weather_data = response.json()
            
            print(f"✅ Weather data fetched successfully")
            print(f"   Timezone: {weather_data.get('timezone', 'Unknown')}")
            print(f"   Forecast days: {len(weather_data.get('daily', {}).get('time', []))}")
            if include_hourly:
                hourly_points = len(weather_data.get('hourly', {}).get('time', []))
                print(f"   Hourly data points: {hourly_points}")
            
            return weather_data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Weather API request failed: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected weather API error: {e}")
            return None
    
    def get_tomorrow_temperature(self, city: str = None, region: str = "Lazio", country: str = "Italy") -> Optional[float]:
        """
        Get tomorrow's average temperature for a specific location
        
        Args:
            city: City name (defaults to Roma if None)
            region: Region name (default "Lazio")
            country: Country name (default "Italy")
            
        Returns:
            Tomorrow's average temperature in Celsius or None if failed
        """
        # Use default city if none provided
        if city is None:
            city = self.default_location['city']
        
        print(f"\n🌡️  Getting tomorrow's temperature for {city}, {region}, {country}")
        print("-" * 60)
        
        # Get coordinates
        coordinates = self.get_coordinates(city, region, country)
        
        if coordinates is None:
            print("⚠️  Geocoding failed, using default coordinates for Roma, Lazio")
            coordinates = self.get_default_coordinates()
        
        # Fetch weather data
        weather_data = self.fetch_weather_forecast(coordinates[0], coordinates[1], days=3)
        
        if weather_data is None:
            print("❌ Failed to fetch weather data")
            return None
        
        try:
            # Extract tomorrow's temperature
            daily_data = weather_data['daily']
            dates = daily_data['time']
            temps_mean = daily_data.get('temperature_2m_mean', [])
            temps_max = daily_data.get('temperature_2m_max', [])
            temps_min = daily_data.get('temperature_2m_min', [])
            
            # Get tomorrow's date
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
            # Find tomorrow's temperature
            tomorrow_temp = None
            for i, date in enumerate(dates):
                if date == tomorrow:
                    if temps_mean and i < len(temps_mean):
                        tomorrow_temp = temps_mean[i]
                    elif temps_max and temps_min and i < len(temps_max) and i < len(temps_min):
                        # Calculate average if mean not available
                        tomorrow_temp = (temps_max[i] + temps_min[i]) / 2
                    break
            
            if tomorrow_temp is not None:
                print(f"✅ Tomorrow's temperature ({tomorrow}): {tomorrow_temp:.1f}°C")
                
                # Show additional info if available
                if len(dates) > 0:
                    print(f"   Forecast location: {weather_data.get('timezone', 'Unknown')}")
                    if temps_max and temps_min:
                        idx = dates.index(tomorrow) if tomorrow in dates else 0
                        if idx < len(temps_max) and idx < len(temps_min):
                            print(f"   Temperature range: {temps_min[idx]:.1f}°C - {temps_max[idx]:.1f}°C")
                
                return tomorrow_temp
            else:
                print(f"❌ Tomorrow's temperature not found in forecast data")
                return None
                
        except (KeyError, IndexError, ValueError) as e:
            print(f"❌ Error parsing weather data: {e}")
            return None
    
    def get_tomorrow_noon_temperature(self, city: str = None, region: str = "Lazio", country: str = "Italy") -> Optional[float]:
        """
        Get tomorrow's temperature specifically at noon (12:00 PM) for more precise EDA analysis
        
        TEMPERATURE-ELECTRICITY DEMAND CORRELATION ANALYSIS:
        
        Why noon temperature is strategic for EDA:
        - Noon represents peak daily temperature (highest heat of the day)
        - Summer pattern: High noon temp → High afternoon/evening electricity demand (A/C cooling)
        - Winter pattern: Low noon temp → High evening/night electricity demand (heating)
        - Noon temperature = 50% of daily cycle, good predictor for peak demand periods
        
        Seasonal electricity demand patterns:
        • SUMMER: Peak demand in afternoons/evenings due to cooling needs
          - Noon temp predicts afternoon A/C load
          - Higher noon temp → Higher evening electricity consumption
        • WINTER: Peak demand at nights due to heating needs  
          - Lower noon temp → Higher evening/night heating load
          - Inverse correlation: colder noon → more evening electricity
        
        Args:
            city: City name (defaults to Roma if None)
            region: Region name (default "Lazio")
            country: Country name (default "Italy")
            
        Returns:
            Tomorrow's noon temperature in Celsius or None if failed
        """
        # Use default city if none provided
        if city is None:
            city = self.default_location['city']
        
        print(f"\n🌞 Getting tomorrow's NOON temperature for {city}, {region}, {country}")
        print("-" * 70)
        
        # Get coordinates
        coordinates = self.get_coordinates(city, region, country)
        
        if coordinates is None:
            print("⚠️  Geocoding failed, using default coordinates for Roma, Lazio")
            coordinates = self.get_default_coordinates()
        
        # Fetch weather data with hourly information
        weather_data = self.fetch_weather_forecast(coordinates[0], coordinates[1], days=2, include_hourly=True)
        
        if weather_data is None:
            print("❌ Failed to fetch hourly weather data")
            # Fallback to daily average
            print("📊 Falling back to daily average temperature...")
            return self.get_tomorrow_temperature(city, region, country)
        
        try:
            # Extract hourly temperature data
            hourly_data = weather_data.get('hourly', {})
            hourly_times = hourly_data.get('time', [])
            hourly_temps = hourly_data.get('temperature_2m', [])
            
            if not hourly_times or not hourly_temps:
                print("⚠️  No hourly data available, falling back to daily average")
                return self.get_tomorrow_temperature(city, region, country)
            
            # Get tomorrow's date and find noon time (12:00)
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            target_noon_time = f"{tomorrow}T12:00"
            
            # Find the closest time to noon tomorrow
            noon_temp = None
            closest_time_diff = float('inf')
            
            for i, time_str in enumerate(hourly_times):
                if time_str.startswith(tomorrow) and i < len(hourly_temps):
                    # Parse the hour from the time string
                    try:
                        hour = int(time_str.split('T')[1].split(':')[0])
                        time_diff = abs(hour - 12)  # Difference from noon
                        
                        if time_diff < closest_time_diff:
                            closest_time_diff = time_diff
                            noon_temp = hourly_temps[i]
                            actual_time = time_str
                    except (ValueError, IndexError):
                        continue
            
            if noon_temp is not None:
                print(f"✅ Tomorrow's noon temperature ({actual_time}): {noon_temp:.1f}°C")
                if closest_time_diff > 0:
                    print(f"   📍 Closest available time: {actual_time} (±{closest_time_diff}h from noon)")
                else:
                    print(f"   🎯 Exact noon temperature retrieved")
                
                # Show temperature context
                print(f"   🌍 Location: {weather_data.get('timezone', 'Unknown')}")
                return noon_temp
            else:
                print(f"❌ Tomorrow's noon temperature not found in hourly data")
                print("📊 Falling back to daily average temperature...")
                return self.get_tomorrow_temperature(city, region, country)
                
        except (KeyError, IndexError, ValueError) as e:
            print(f"❌ Error parsing hourly weather data: {e}")
            print("📊 Falling back to daily average temperature...")
            return self.get_tomorrow_temperature(city, region, country)
    
    def analyze_seasonal_correlation_pattern(self, noon_temp: float, season: str = None) -> Dict:
        """
        Analyze expected electricity demand pattern based on noon temperature and season
        
        Based on user insights:
        - Noon/afternoon = highest temperatures in a day
        - Night = lower temperatures  
        - Summer: Higher demand in afternoons/evenings due to hot weather (cooling)
        - Winter: Higher demand at night due to lower temperatures (heating)
        - Noon temperature (50% of day) = good predictor for peak demand periods
        
        Args:
            noon_temp: Noon temperature in Celsius
            season: Season name (auto-detected if None)
            
        Returns:
            Dictionary with correlation analysis and demand predictions
        """
        # Auto-detect season if not provided
        if season is None:
            current_month = datetime.now().month
            if current_month in [12, 1, 2]:
                season = "winter"
            elif current_month in [3, 4, 5]:
                season = "spring"
            elif current_month in [6, 7, 8]:
                season = "summer"
            else:
                season = "autumn"
        
        analysis = {
            'noon_temperature': noon_temp,
            'season': season,
            'correlation_type': None,
            'peak_demand_time': None,
            'expected_load_pattern': None,
            'correlation_strength': None
        }
        
        if season == "summer":
            if noon_temp > 25:  # Hot summer day
                analysis.update({
                    'correlation_type': 'positive_strong',
                    'peak_demand_time': 'afternoon_evening (14:00-20:00)',
                    'expected_load_pattern': 'high_cooling_demand',
                    'correlation_strength': 'strong (r ≈ +0.7 to +0.8)',
                    'demand_driver': 'air_conditioning',
                    'load_increase': f'{(noon_temp - 25) * 2:.0f}% above baseline',
                    'pattern_explanation': 'Hot noon → Hot afternoon → High A/C demand'
                })
            elif noon_temp > 20:  # Moderate summer day
                analysis.update({
                    'correlation_type': 'positive_moderate',
                    'peak_demand_time': 'late_afternoon (16:00-18:00)',
                    'expected_load_pattern': 'moderate_cooling_demand',
                    'correlation_strength': 'moderate (r ≈ +0.4 to +0.6)',
                    'demand_driver': 'ventilation_fans',
                    'load_increase': f'{(noon_temp - 20) * 1:.0f}% above baseline',
                    'pattern_explanation': 'Warm noon → Comfortable afternoon → Moderate cooling'
                })
            else:  # Cool summer day
                analysis.update({
                    'correlation_type': 'minimal',
                    'peak_demand_time': 'evening (18:00-21:00)',
                    'expected_load_pattern': 'baseline_consumption',
                    'correlation_strength': 'weak (r ≈ +0.1 to +0.3)',
                    'demand_driver': 'normal_activities',
                    'load_increase': '0% - baseline level',
                    'pattern_explanation': 'Cool noon → Comfortable day → Normal consumption'
                })
                
        elif season == "winter":
            if noon_temp < 5:  # Very cold winter day
                analysis.update({
                    'correlation_type': 'negative_strong',
                    'peak_demand_time': 'evening_night (18:00-22:00)',
                    'expected_load_pattern': 'high_heating_demand',
                    'correlation_strength': 'strong (r ≈ -0.6 to -0.8)',
                    'demand_driver': 'electric_heating',
                    'load_increase': f'{(5 - noon_temp) * 3:.0f}% above baseline',
                    'pattern_explanation': 'Cold noon → Colder night → High heating demand'
                })
            elif noon_temp < 12:  # Cold winter day
                analysis.update({
                    'correlation_type': 'negative_moderate',
                    'peak_demand_time': 'evening (17:00-20:00)',
                    'expected_load_pattern': 'moderate_heating_demand',
                    'correlation_strength': 'moderate (r ≈ -0.3 to -0.5)',
                    'demand_driver': 'supplemental_heating',
                    'load_increase': f'{(12 - noon_temp) * 1.5:.0f}% above baseline',
                    'pattern_explanation': 'Cool noon → Cold evening → Moderate heating'
                })
            else:  # Mild winter day
                analysis.update({
                    'correlation_type': 'minimal',
                    'peak_demand_time': 'evening (19:00-21:00)',
                    'expected_load_pattern': 'baseline_consumption',
                    'correlation_strength': 'weak (r ≈ -0.1 to -0.2)',
                    'demand_driver': 'lighting_electronics',
                    'load_increase': '0% - baseline level',
                    'pattern_explanation': 'Mild noon → Comfortable evening → Normal consumption'
                })
                
        else:  # Spring/Autumn - transitional seasons
            analysis.update({
                'correlation_type': 'u_shaped_weak',
                'peak_demand_time': 'evening (18:00-21:00)',
                'expected_load_pattern': 'stable_consumption',
                'correlation_strength': 'weak (r ≈ +0.1 to +0.3)',
                'demand_driver': 'minimal_heating_cooling',
                'load_increase': '0-5% above baseline',
                'pattern_explanation': 'Transitional weather → Stable consumption patterns'
            })
        
        return analysis
    
    def get_current_weather(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Get current weather conditions
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Current weather data dictionary or None if failed
        """
        try:
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'current_weather': True,
                'timezone': 'Europe/Rome'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"❌ Current weather request failed: {e}")
            return None
    
    def get_extended_forecast(self, city: str = None, days: int = 7) -> Optional[Dict]:
        """
        Get extended weather forecast for multiple days
        
        Args:
            city: City name (defaults to Roma)
            days: Number of forecast days
            
        Returns:
            Extended forecast data or None if failed
        """
        if city is None:
            city = self.default_location['city']
        
        print(f"Getting {days}-day forecast for {city}, Lazio, Italy")
        
        # Get coordinates
        coordinates = self.get_coordinates(city, "Lazio", "Italy")
        
        if coordinates is None:
            coordinates = self.get_default_coordinates()
        
        # Fetch extended forecast
        weather_data = self.fetch_weather_forecast(coordinates[0], coordinates[1], days)
        
        if weather_data:
            print(f"✅ Extended forecast retrieved for {days} days")
            return weather_data
        else:
            print(f"❌ Failed to get extended forecast")
            return None

class WeatherDataProcessor:
    """
    Process weather data for electricity forecasting models
    """
    
    def __init__(self):
        self.weather_service = WeatherService()
    
    def prepare_forecast_input(self, historical_data: list, city: str = None, use_noon_temp: bool = True) -> Optional[Dict]:
        """
        Prepare complete input data for electricity forecasting including tomorrow's weather
        
        Args:
            historical_data: List of historical electricity consumption and weather data
            city: City name for weather forecast (optional)
            use_noon_temp: Whether to use noon temperature for better EDA analysis (default True)
            
        Returns:
            Complete input data dictionary ready for model prediction
        """
        print("\n🔮 Preparing forecast input with real-time weather data")
        print("=" * 60)
        
        # Choose temperature method based on use_noon_temp flag
        if use_noon_temp:
            print("🌞 Using noon temperature for more precise EDA analysis")
            tomorrow_temp = self.weather_service.get_tomorrow_noon_temperature(city)
            temp_type = "noon_temperature"
        else:
            print("📊 Using daily average temperature")
            tomorrow_temp = self.weather_service.get_tomorrow_temperature(city)
            temp_type = "daily_average"
        
        if tomorrow_temp is None:
            print("⚠️  Using fallback temperature estimation")
            # Fallback: use recent temperature trend
            if historical_data and len(historical_data) > 0:
                recent_temps = [item.get('temperature', 15) for item in historical_data[-7:]]
                tomorrow_temp = sum(recent_temps) / len(recent_temps)
                print(f"   Estimated temperature based on recent data: {tomorrow_temp:.1f}°C")
            else:
                tomorrow_temp = 15.0  # Default reasonable temperature
                print(f"   Using default temperature: {tomorrow_temp:.1f}°C")
            temp_type = "estimated"
        
        # Prepare complete forecast input
        forecast_input = {
            'historical_data': historical_data,
            'next_day_temperature': tomorrow_temp,
            'temperature_type': temp_type,
            'weather_source': 'open_meteo_api',
            'forecast_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'generated_at': datetime.now().isoformat()
        }
        
        # Add seasonal correlation analysis if using noon temperature
        if use_noon_temp and tomorrow_temp is not None:
            correlation_analysis = self.weather_service.analyze_seasonal_correlation_pattern(tomorrow_temp)
            forecast_input['correlation_analysis'] = correlation_analysis
            
            print(f"📊 Correlation Analysis:")
            print(f"   Season: {correlation_analysis['season']}")
            print(f"   Correlation type: {correlation_analysis['correlation_type']}")
            print(f"   Peak demand time: {correlation_analysis['peak_demand_time']}")
            print(f"   Expected pattern: {correlation_analysis['expected_load_pattern']}")
            print(f"   Pattern explanation: {correlation_analysis.get('pattern_explanation', 'N/A')}")
        
        print(f"✅ Forecast input prepared:")
        print(f"   Historical records: {len(historical_data)}")
        print(f"   Next day temperature: {tomorrow_temp:.1f}°C")
        print(f"   Temperature type: {temp_type}")
        print(f"   Forecast date: {forecast_input['forecast_date']}")
        
        return forecast_input

def test_weather_service():
    """
    Test function for the weather service
    """
    print("🧪 TESTING WEATHER SERVICE")
    print("=" * 40)
    
    weather_service = WeatherService()
    
    # Test 1: Geocoding
    print("\n1. Testing geocoding...")
    coords = weather_service.get_coordinates("Roma", "Lazio", "Italy")
    if coords:
        print(f"✅ Roma coordinates: {coords}")
    else:
        print("❌ Geocoding failed")
    
    # Test 2: Weather forecast
    print("\n2. Testing weather forecast...")
    if coords:
        weather_data = weather_service.fetch_weather_forecast(coords[0], coords[1], 3)
        if weather_data:
            print("✅ Weather forecast retrieved")
            daily_data = weather_data.get('daily', {})
            if 'time' in daily_data:
                print(f"   Forecast dates: {daily_data['time']}")
        else:
            print("❌ Weather forecast failed")
    
    # Test 3: Tomorrow's temperature
    print("\n3. Testing tomorrow's temperature...")
    tomorrow_temp = weather_service.get_tomorrow_temperature("Roma")
    if tomorrow_temp:
        print(f"✅ Tomorrow's temperature: {tomorrow_temp}°C")
    else:
        print("❌ Tomorrow's temperature failed")
    
    # Test 4: Weather data processor with seasonal analysis
    print("\n4. Testing weather data processor with seasonal correlation analysis...")
    processor = WeatherDataProcessor()
    
    # Sample historical data
    sample_historical = [
        {"date": "2024-12-25", "load": 14500, "temperature": 8.5},
        {"date": "2024-12-26", "load": 15200, "temperature": 6.2},
        {"date": "2024-12-27", "load": 14800, "temperature": 7.1}
    ]
    
    forecast_input = processor.prepare_forecast_input(sample_historical, "Roma", use_noon_temp=True)
    if forecast_input:
        print("✅ Forecast input prepared successfully")
        print(f"   Temperature source: {forecast_input.get('weather_source')}")
        print(f"   Temperature type: {forecast_input.get('temperature_type')}")
        
        # Show correlation analysis if available
        if 'correlation_analysis' in forecast_input:
            analysis = forecast_input['correlation_analysis']
            print(f"\n📊 Seasonal Correlation Analysis:")
            print(f"   Season: {analysis['season']}")
            print(f"   Peak demand time: {analysis['peak_demand_time']}")
            print(f"   Correlation strength: {analysis['correlation_strength']}")
            print(f"   Load increase: {analysis.get('load_increase', 'N/A')}")
    else:
        print("❌ Forecast input preparation failed")
    
    # Test 5: Direct seasonal correlation analysis
    print("\n5. Testing seasonal correlation patterns...")
    weather_service = WeatherService()
    
    # Test different temperature scenarios
    test_scenarios = [
        {"temp": 30, "season": "summer", "desc": "Hot summer day"},
        {"temp": 2, "season": "winter", "desc": "Very cold winter day"},
        {"temp": 18, "season": "spring", "desc": "Mild spring day"}
    ]
    
    for scenario in test_scenarios:
        analysis = weather_service.analyze_seasonal_correlation_pattern(
            scenario["temp"], scenario["season"]
        )
        print(f"\n🌡️  {scenario['desc']} ({scenario['temp']}°C):")
        print(f"   Correlation: {analysis['correlation_type']}")
        print(f"   Peak time: {analysis['peak_demand_time']}")
        print(f"   Driver: {analysis['demand_driver']}")
        print(f"   Load change: {analysis.get('load_increase', 'N/A')}")
        print(f"   Explanation: {analysis.get('pattern_explanation', 'N/A')}")

if __name__ == "__main__":
    test_weather_service()
