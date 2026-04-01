package com.example.springaidemo.tools;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Description;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Function;

/**
 * Configuration for Function/Tool Calling
 * 
 * Tool calling (also known as function calling) allows the AI model to
 * interact with external APIs and tools to perform actions or retrieve information
 * 
 * Reference: https://docs.spring.io/spring-ai/reference/api/tools.html
 */
@Configuration
public class ToolConfiguration {

    /**
     * Example Tool: Get current date and time
     * The model can call this function to get the current date/time
     */
    @Bean
    @Description("Get the current date and time")
    public Function<DateTimeRequest, DateTimeResponse> getCurrentDateTime() {
        return request -> {
            LocalDateTime now = LocalDateTime.now();
            String formatted = now.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
            return new DateTimeResponse(formatted, request.timezone());
        };
    }

    /**
     * Example Tool: Weather information (mock implementation)
     */
    @Bean
    @Description("Get weather information for a specific location")
    public Function<WeatherRequest, WeatherResponse> getWeather() {
        return request -> {
            // Mock weather data - in production, call a real weather API
            Map<String, String> weatherData = new HashMap<>();
            weatherData.put("London", "Cloudy, 15°C");
            weatherData.put("New York", "Sunny, 22°C");
            weatherData.put("Tokyo", "Rainy, 18°C");
            
            String weather = weatherData.getOrDefault(request.location(), "Unknown location");
            return new WeatherResponse(request.location(), weather);
        };
    }

    /**
     * Example Tool: Calculate mathematical expressions
     */
    @Bean
    @Description("Calculate mathematical expressions")
    public Function<CalculationRequest, CalculationResponse> calculate() {
        return request -> {
            try {
                // Simple calculator - in production, use a proper expression evaluator
                double result = evaluateSimpleExpression(request.expression());
                return new CalculationResponse(request.expression(), result, true);
            } catch (Exception e) {
                return new CalculationResponse(request.expression(), 0.0, false);
            }
        };
    }

    /**
     * Example of using tools with ChatClient
     * This is not a bean, but shows how to use tools in your code
     */
    public String exampleToolUsage(ChatClient chatClient) {
        return chatClient.prompt()
                .user("What's the weather in London and what time is it?")
                .functions("getCurrentDateTime", "getWeather") // Specify which tools to use
                .call()
                .content();
    }

    // Helper method for simple calculation
    private double evaluateSimpleExpression(String expression) {
        // Very basic implementation - use a library like exp4j in production
        expression = expression.replaceAll("\\s+", "");
        if (expression.contains("+")) {
            String[] parts = expression.split("\\+");
            return Double.parseDouble(parts[0]) + Double.parseDouble(parts[1]);
        } else if (expression.contains("-")) {
            String[] parts = expression.split("-");
            return Double.parseDouble(parts[0]) - Double.parseDouble(parts[1]);
        } else if (expression.contains("*")) {
            String[] parts = expression.split("\\*");
            return Double.parseDouble(parts[0]) * Double.parseDouble(parts[1]);
        } else if (expression.contains("/")) {
            String[] parts = expression.split("/");
            return Double.parseDouble(parts[0]) / Double.parseDouble(parts[1]);
        }
        return Double.parseDouble(expression);
    }

    // Request/Response records for tools
    public record DateTimeRequest(String timezone) {}
    public record DateTimeResponse(String dateTime, String timezone) {}
    
    public record WeatherRequest(String location) {}
    public record WeatherResponse(String location, String weather) {}
    
    public record CalculationRequest(String expression) {}
    public record CalculationResponse(String expression, double result, boolean success) {}
}
