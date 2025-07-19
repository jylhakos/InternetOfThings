/**
 * LangChain.js Tools Implementation
 * Provides weather information and geolocation tools for the AI Agent
 */

import { DynamicStructuredTool } from '@langchain/core/tools';
import { z } from 'zod';
import axios from 'axios';
import 'dotenv/config';

/**
 * Weather Tool for fetching weather information using Open-Meteo API
 * This tool handles both geocoding and weather data retrieval
 */
export class WeatherTool extends DynamicStructuredTool {
  constructor() {
    super({
      name: 'get_weather_info',
      description: 'Get current weather information for a specific city. Provides temperature, weather conditions, and location details.',
      schema: z.object({
        city: z.string().describe('The name of the city to get weather for'),
      }),
      func: async ({ city }) => {
        try {
          // First, get coordinates for the city
          const coordinates = await this.getCoordinates(city);
          if (!coordinates) {
            return `Sorry, I couldn't find the location '${city}'. Please check the city name and try again.`;
          }

          // Then get weather data
          const weatherData = await this.getWeatherData(
            coordinates.latitude, 
            coordinates.longitude
          );

          if (!weatherData) {
            return `Sorry, I couldn't retrieve weather data for ${coordinates.name}.`;
          }

          // Format the response
          const temperature = weatherData.temperature;
          const unit = weatherData.temperature_unit || '°C';
          const weatherCode = weatherData.weathercode;
          const windSpeed = weatherData.windspeed;
          const windUnit = weatherData.windspeed_unit || 'km/h';

          return `Current weather in ${coordinates.name}, ${coordinates.country}:
🌡️ Temperature: ${temperature}${unit}
🌤️ Conditions: ${this.getWeatherDescription(weatherCode)}
💨 Wind Speed: ${windSpeed} ${windUnit}
📍 Location: ${coordinates.latitude}°N, ${coordinates.longitude}°E`;

        } catch (error) {
          console.error('Weather tool error:', error);
          return `Sorry, I encountered an error while fetching weather data for ${city}. Please try again later.`;
        }
      },
    });

    this.geocodingUrl = process.env.OPEN_METEO_GEOCODING_URL || 'https://geocoding-api.open-meteo.com/v1/search';
    this.weatherUrl = process.env.OPEN_METEO_WEATHER_URL || 'https://api.open-meteo.com/v1/forecast';
  }

  /**
   * Get latitude and longitude coordinates for a city
   */
  async getCoordinates(cityName) {
    try {
      const response = await axios.get(this.geocodingUrl, {
        params: {
          name: cityName,
          count: 1,
          language: 'en',
          format: 'json'
        },
        timeout: 10000
      });

      const data = response.data;
      if (data.results && data.results.length > 0) {
        const result = data.results[0];
        return {
          latitude: result.latitude,
          longitude: result.longitude,
          name: result.name,
          country: result.country || ''
        };
      }
      return null;
    } catch (error) {
      console.error(`Error getting coordinates for ${cityName}:`, error.message);
      return null;
    }
  }

  /**
   * Get weather data using coordinates
   */
  async getWeatherData(latitude, longitude) {
    try {
      const response = await axios.get(this.weatherUrl, {
        params: {
          latitude: latitude,
          longitude: longitude,
          current_weather: true,
          timezone: 'auto'
        },
        timeout: 10000
      });

      return response.data.current_weather;
    } catch (error) {
      console.error('Error getting weather data:', error.message);
      return null;
    }
  }

  /**
   * Convert weather code to human-readable description
   */
  getWeatherDescription(code) {
    const weatherCodes = {
      0: 'Clear sky',
      1: 'Mainly clear',
      2: 'Partly cloudy',
      3: 'Overcast',
      45: 'Fog',
      48: 'Depositing rime fog',
      51: 'Light drizzle',
      53: 'Moderate drizzle',
      55: 'Dense drizzle',
      61: 'Slight rain',
      63: 'Moderate rain',
      65: 'Heavy rain',
      71: 'Slight snow fall',
      73: 'Moderate snow fall',
      75: 'Heavy snow fall',
      77: 'Snow grains',
      80: 'Slight rain showers',
      81: 'Moderate rain showers',
      82: 'Violent rain showers',
      85: 'Slight snow showers',
      86: 'Heavy snow showers',
      95: 'Thunderstorm',
      96: 'Thunderstorm with slight hail',
      99: 'Thunderstorm with heavy hail'
    };

    return weatherCodes[code] || 'Unknown weather condition';
  }
}

/**
 * Greeting Tool for handling greeting interactions
 */
export class GreetingTool extends DynamicStructuredTool {
  constructor() {
    super({
      name: 'handle_greeting',
      description: 'Handle greeting messages and provide appropriate responses',
      schema: z.object({
        greeting: z.string().describe('The greeting message from the user'),
      }),
      func: async ({ greeting }) => {
        const greetingPatterns = {
          morning: ['good morning', 'morning'],
          afternoon: ['good afternoon', 'afternoon'],
          evening: ['good evening', 'evening'],
          night: ['good night', 'night'],
          general: ['hello', 'hi', 'hey', 'greetings', 'howdy']
        };

        const lowerGreeting = greeting.toLowerCase();
        
        // Check for specific time-based greetings
        for (const [timeOfDay, patterns] of Object.entries(greetingPatterns)) {
          if (patterns.some(pattern => lowerGreeting.includes(pattern))) {
            if (timeOfDay === 'morning') {
              return "Good morning! 🌅 I hope you're having a wonderful start to your day. How can I assist you today?";
            } else if (timeOfDay === 'afternoon') {
              return "Good afternoon! ☀️ I hope your day is going well. What can I help you with?";
            } else if (timeOfDay === 'evening') {
              return "Good evening! 🌆 I hope you've had a great day. How may I assist you this evening?";
            } else if (timeOfDay === 'night') {
              return "Good night! 🌙 I hope you have a restful night. Is there anything I can help you with before you rest?";
            } else if (timeOfDay === 'general') {
              return "Hello! 👋 It's great to meet you! I'm your AI assistant, ready to help with questions, weather information, or just have a friendly chat. What would you like to know?";
            }
          }
        }

        // Default friendly response
        return "Hello there! 😊 I'm your AI assistant powered by LangChain.js. I can help you with various tasks including weather information, answer questions, or just have a conversation. What can I do for you today?";
      },
    });
  }
}

/**
 * Location Tool for getting detailed location information
 */
export class LocationTool extends DynamicStructuredTool {
  constructor() {
    super({
      name: 'get_location_info',
      description: 'Get detailed location information including coordinates, timezone, and geographic details for a city',
      schema: z.object({
        city: z.string().describe('The name of the city to get location information for'),
      }),
      func: async ({ city }) => {
        try {
          const geocodingUrl = process.env.OPEN_METEO_GEOCODING_URL || 'https://geocoding-api.open-meteo.com/v1/search';
          
          const response = await axios.get(geocodingUrl, {
            params: {
              name: city,
              count: 5, // Get multiple results for more info
              language: 'en',
              format: 'json'
            },
            timeout: 10000
          });

          const data = response.data;
          if (data.results && data.results.length > 0) {
            const location = data.results[0];
            
            let locationInfo = `📍 Location Information for ${location.name}:
🌍 Country: ${location.country}
🗺️ Coordinates: ${location.latitude}°N, ${location.longitude}°E
🏔️ Elevation: ${location.elevation || 'N/A'}m above sea level`;

            if (location.timezone) {
              locationInfo += `\n🕐 Timezone: ${location.timezone}`;
            }
            if (location.population) {
              locationInfo += `\n👥 Population: ${location.population.toLocaleString()}`;
            }
            if (location.admin1) {
              locationInfo += `\n🏛️ Region: ${location.admin1}`;
            }

            // Add alternative locations if available
            if (data.results.length > 1) {
              locationInfo += `\n\n🔍 Other locations with similar names:`;
              for (let i = 1; i < Math.min(data.results.length, 4); i++) {
                const alt = data.results[i];
                locationInfo += `\n  • ${alt.name}, ${alt.country}`;
              }
            }

            return locationInfo;
          }
          
          return `Sorry, I couldn't find location information for '${city}'. Please check the spelling and try again.`;
          
        } catch (error) {
          console.error('Location tool error:', error);
          return `Sorry, I encountered an error while fetching location data for ${city}. Please try again later.`;
        }
      },
    });
  }
}

/**
 * Tool Manager to handle all available tools
 */
export class ToolManager {
  constructor() {
    this.weatherTool = new WeatherTool();
    this.greetingTool = new GreetingTool();
    this.locationTool = new LocationTool();
  }

  /**
   * Get all available tools as an array
   */
  getAllTools() {
    return [
      this.weatherTool,
      this.greetingTool,
      this.locationTool
    ];
  }

  /**
   * Get tool by name
   */
  getTool(toolName) {
    const toolMap = {
      'get_weather_info': this.weatherTool,
      'handle_greeting': this.greetingTool,
      'get_location_info': this.locationTool
    };
    return toolMap[toolName];
  }

  /**
   * Determine which tool to use based on user input
   */
  async determineToolFromInput(userInput) {
    const input = userInput.toLowerCase();
    
    // Check for weather-related keywords
    if (input.includes('weather') || input.includes('temperature') || 
        input.includes('temp') || input.includes('climate') ||
        input.includes('forecast') || input.includes('rain') ||
        input.includes('snow') || input.includes('sunny') ||
        input.includes('cloudy') || input.includes('wind')) {
      return 'weather';
    }
    
    // Check for greeting keywords
    if (input.includes('hello') || input.includes('hi') || 
        input.includes('hey') || input.includes('good morning') ||
        input.includes('good afternoon') || input.includes('good evening') ||
        input.includes('good night') || input.includes('greetings') ||
        input.includes('howdy')) {
      return 'greeting';
    }
    
    // Check for location-related keywords
    if (input.includes('location') || input.includes('coordinates') ||
        input.includes('latitude') || input.includes('longitude') ||
        input.includes('where is') || input.includes('timezone') ||
        input.includes('elevation')) {
      return 'location';
    }
    
    return 'llm'; // Default to LLM for other queries
  }
}