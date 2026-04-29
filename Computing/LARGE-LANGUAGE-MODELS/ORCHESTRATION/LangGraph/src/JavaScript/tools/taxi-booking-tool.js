import { tool } from "@langchain/core/tools";
import { z } from "zod";
import axios from "axios";

/**
 * Geocoding Tool for converting city names to coordinates
 * Uses MapTiler Geocoding API
 */
const geocodingSchema = z.object({
  city: z.string().describe("The name of the city (e.g., London, Berlin)"),
});

export const geocodingTool = tool(
  async ({ city }) => {
    try {
      // Mock implementation - in production, you would use a real geocoding API
      const mockCoordinates = {
        "london": { lat: 51.5074, lng: -0.1278, country: "UK" },
        "berlin": { lat: 52.5200, lng: 13.4050, country: "Germany" },
        "paris": { lat: 48.8566, lng: 2.3522, country: "France" },
        "madrid": { lat: 40.4168, lng: -3.7038, country: "Spain" },
        "rome": { lat: 41.9028, lng: 12.4964, country: "Italy" }
      };
      
      const cityKey = city.toLowerCase();
      if (mockCoordinates[cityKey]) {
        const coords = mockCoordinates[cityKey];
        return `Location found: ${city} - Latitude: ${coords.lat}, Longitude: ${coords.lng}, Country: ${coords.country}`;
      } else {
        return `Location not found for: ${city}. Supported cities: London, Berlin, Paris, Madrid, Rome`;
      }
    } catch (error) {
      return `Error geocoding ${city}: ${error.message}`;
    }
  },
  {
    name: "geocodingTool",
    description: "Get coordinates for a city using geocoding service",
    schema: geocodingSchema,
  }
);

/**
 * Taxi Booking Tool
 * Simulates booking a taxi using a taxi API service
 */
const taxiBookingSchema = z.object({
  city: z.string().describe("The city where the taxi is needed"),
  pickup_address: z.string().describe("Pickup address or location"),
  destination_address: z.string().describe("Destination address or location"),
  passenger_count: z.number().min(1).max(8).describe("Number of passengers (1-8)"),
  taxi_type: z.enum(["economy", "premium", "luxury", "van"]).describe("Type of taxi service"),
  booking_time: z.string().optional().describe("Preferred booking time (ISO string, optional for immediate booking)")
});

export const taxiBookingTool = tool(
  async ({ city, pickup_address, destination_address, passenger_count, taxi_type, booking_time }) => {
    try {
      // Mock taxi booking API call
      const bookingId = `taxi_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const estimatedTime = Math.floor(Math.random() * 15) + 5; // 5-20 minutes
      const estimatedCost = calculateEstimatedCost(city, taxi_type, passenger_count);
      
      // Simulate API response
      const bookingResponse = {
        success: true,
        booking_id: bookingId,
        city: city,
        pickup: pickup_address,
        destination: destination_address,
        passengers: passenger_count,
        taxi_type: taxi_type,
        estimated_arrival: `${estimatedTime} minutes`,
        estimated_cost: estimatedCost,
        booking_time: booking_time || new Date().toISOString(),
        driver_info: {
          name: "John Doe",
          phone: "+44-xxx-xxx-xxxx",
          vehicle: "Toyota Prius - ABC 123"
        },
        status: "confirmed"
      };

      return `✅ Taxi booked successfully!
📍 City: ${bookingResponse.city}
🚗 Booking ID: ${bookingResponse.booking_id}
👥 Passengers: ${bookingResponse.passengers}
🎯 Type: ${bookingResponse.taxi_type}
📍 From: ${bookingResponse.pickup}
📍 To: ${bookingResponse.destination}
⏰ Estimated arrival: ${bookingResponse.estimated_arrival}
💰 Estimated cost: ${bookingResponse.estimated_cost}
👨‍✈️ Driver: ${bookingResponse.driver_info.name}
📞 Contact: ${bookingResponse.driver_info.phone}
🚙 Vehicle: ${bookingResponse.driver_info.vehicle}
📅 Status: ${bookingResponse.status.toUpperCase()}`;
      
    } catch (error) {
      return `❌ Failed to book taxi: ${error.message}`;
    }
  },
  {
    name: "bookTaxi",
    description: "Book a taxi in supported cities (London, Berlin, Paris, Madrid, Rome)",
    schema: taxiBookingSchema,
  }
);

/**
 * Calculate estimated cost based on city, taxi type, and passenger count
 */
function calculateEstimatedCost(city, taxiType, passengerCount) {
  const basePrices = {
    "london": { economy: 12, premium: 18, luxury: 30, van: 25 },
    "berlin": { economy: 8, premium: 14, luxury: 25, van: 20 },
    "paris": { economy: 10, premium: 16, luxury: 28, van: 22 },
    "madrid": { economy: 7, premium: 12, luxury: 20, van: 18 },
    "rome": { economy: 9, premium: 15, luxury: 26, van: 21 }
  };

  const cityKey = city.toLowerCase();
  const basePrice = basePrices[cityKey]?.[taxiType] || 15;
  const passengerMultiplier = passengerCount > 4 ? 1.2 : 1.0;
  const finalPrice = Math.round(basePrice * passengerMultiplier * (1 + Math.random() * 0.3)); // Add some variance
  
  return `${getCurrencySymbol(cityKey)}${finalPrice}`;
}

/**
 * Get currency symbol for the city
 */
function getCurrencySymbol(cityKey) {
  const currencies = {
    "london": "£",
    "berlin": "€",
    "paris": "€",
    "madrid": "€",
    "rome": "€"
  };
  return currencies[cityKey] || "$";
}

/**
 * Taxi Status Tool
 * Check the status of an existing taxi booking
 */
const taxiStatusSchema = z.object({
  booking_id: z.string().describe("The booking ID to check status for"),
});

export const taxiStatusTool = tool(
  async ({ booking_id }) => {
    try {
      // Mock status check
      const statuses = ["confirmed", "driver_assigned", "en_route", "arrived", "completed", "cancelled"];
      const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
      
      const statusInfo = {
        booking_id,
        status: randomStatus,
        estimated_arrival: randomStatus === "en_route" ? "3 minutes" : 
                          randomStatus === "arrived" ? "Driver waiting" :
                          randomStatus === "driver_assigned" ? "8 minutes" : "N/A",
        driver_location: randomStatus === "en_route" ? "2.1 km away" : "N/A",
        message: getStatusMessage(randomStatus)
      };

      return `🚗 Taxi Status Update
📋 Booking ID: ${statusInfo.booking_id}
📊 Status: ${statusInfo.status.toUpperCase()}
⏰ ETA: ${statusInfo.estimated_arrival}
📍 Driver location: ${statusInfo.driver_location}
💬 ${statusInfo.message}`;
      
    } catch (error) {
      return `❌ Failed to get taxi status: ${error.message}`;
    }
  },
  {
    name: "checkTaxiStatus",
    description: "Check the status of an existing taxi booking",
    schema: taxiStatusSchema,
  }
);

function getStatusMessage(status) {
  const messages = {
    "confirmed": "Your booking is confirmed. Looking for a driver...",
    "driver_assigned": "Driver assigned! They're on their way to pick you up.",
    "en_route": "Driver is en route to your pickup location.",
    "arrived": "Driver has arrived at pickup location. Please look for the vehicle.",
    "completed": "Trip completed successfully. Thank you for riding with us!",
    "cancelled": "Booking was cancelled."
  };
  return messages[status] || "Status unknown";
}

// Export all taxi-related tools
export const taxiTools = [
  geocodingTool,
  taxiBookingTool,
  taxiStatusTool
];
