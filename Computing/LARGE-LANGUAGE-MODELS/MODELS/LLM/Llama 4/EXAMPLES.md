# Meta Llama 4 Scout AI Agent usage

This document provides examples of using the AI Agent system with **Meta Llama 4 Scout**, including prompt templates, tool calling capabilities, Open WebUI integration, and CURL API examples.

## Meta Llama 4 Scout features

**Meta Llama 4 Scout** represents the cutting-edge of LLM technology with:
- **10 Million Token Context Window**: Process extremely long documents and conversations
- **Mixture of Experts (MoE) Architecture**: Efficient processing with 8 specialized expert networks
- **Native Tool Calling**: Built-in function calling without complex prompt engineering
- **Enhanced Reasoning**: Advanced logic and problem-solving capabilities
- **Multi-turn Dialogue**: Sophisticated conversation management

## Setup and installation

### Start with Meta Llama 4 Scout

```bash
# 1. Automated setup for Llama 4 Scout
./setup-llama4.sh

# 2. Install and start Ollama with Llama 4 Scout
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &

# 3. Pull Meta Llama 4 Scout model (large download: ~15-20GB)
ollama pull llama4:scout

# Alternative: Quantized version (~10GB)
# ollama pull ingu627/llama4-scout-q4

# 4. Start the AI Agent with Llama 4 Scout
source venv/bin/activate
export MODEL_NAME="llama4:scout"
python src/index.py

# 5. Start Open WebUI for browser interface
./start-webui.sh
```

### Fallback setup with Legacy Llama 3.x

```bash
# For systems that can't run Llama 4 Scout
./setup.sh

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &

# Pull legacy model
ollama pull llama3.1:8b-instruct-q4_0

# Start with legacy configuration
export MODEL_NAME="llama3.1:8b-instruct-q4_0"
python src/index.py
```

## Meta Llama 4 Scout Prompt Templates

### Native Llama 4 Scout format

Meta Llama 4 Scout uses advanced prompt templates with tool integration:

#### System Message Template
```
<|begin_of_text|><|header_start|>system<|header_end|>

You are an advanced AI assistant powered by Meta Llama 4 Scout with the following capabilities:
- 10 million token context window for processing very long conversations
- Mixture of Experts architecture for efficient specialized processing  
- Native tool calling for real-time information access
- Enhanced reasoning and problem-solving abilities

Available tools:
- get_weather(city, metric): Get current weather information for any city worldwide

When a user asks about weather, use the get_weather tool by responding with:
[get_weather(city="<city_name>", metric="celsius")]

You can call multiple tools in a single response for multi-city queries:
[get_weather(city="London", metric="celsius"), get_weather(city="Tokyo", metric="celsius")]

<|eot|><|header_start|>user<|header_end|>

{user_message}<|eot|><|header_start|>assistant<|header_end|>

```

#### Tool Calling response template
```
<|begin_of_text|><|header_start|>user<|header_end|>

What's the weather in London and Paris?<|eot|><|header_start|>assistant<|header_end|>

[get_weather(city="London", metric="celsius"), get_weather(city="Paris", metric="celsius")]<|eot|><|header_start|>ipython<|header_end|>

[
  {"response": "The current temperature in London is 18°C. Partly cloudy conditions."},
  {"response": "The current temperature in Paris is 22°C. Sunny conditions."}
]<|eot|><|header_start|>assistant<|header_end|>

Based on the current weather data:

**London**: 18°C with partly cloudy conditions
**Paris**: 22°C with sunny conditions

Paris is currently warmer than London by 4°C, and Paris has better weather conditions for outdoor activities today.
```

### Legacy Llama 3.x Template (Backward compatibility)

```
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a helpful AI assistant. You can provide weather information by asking the user to specify the city they're interested in.

<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

```

## API testing with Meta Llama 4 Scout

### 1. Health Check with Llama 4 Scout metadata

```bash
curl http://localhost:8000/health
```

**Response (Meta Llama 4 Scout):**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-20T10:30:00Z",
  "services": {
    "llm": "healthy",
    "weather_api": "healthy"
  },
  "agent_info": {
    "name": "AI Agent - Llama 4 Scout",
    "version": "2.0.0",
    "model": "llama4:scout",
    "capabilities": ["chat", "weather", "greetings", "tool_calling", "long_context"],
    "context_window": "10M tokens",
    "architecture": "MoE (Mixture of Experts)",
    "experts": 8
  },
  "llama4_features": {
    "context_window": "10M tokens",
    "tool_calling": true,
    "mixture_of_experts": true,
    "advanced_reasoning": true,
    "multimodal_ready": true
  }
}
```

### 2. Chat Completion - Greeting with Llama 4 Scout

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user", 
        "content": "Hello! I want to test your Meta Llama 4 Scout capabilities. Can you tell me about your advanced features?"
      }
    ],
    "temperature": 0.7,
    "max_tokens": 300
  }'
### 3. Weather Query with Native Tool Calling (Single City)

**Meta Llama 4 Scout automatically detects weather requests and calls appropriate tools:**

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is the current temperature in London?"}
    ],
    "temperature": 0.7,
    "max_tokens": 200
  }'
```

**Response (Tool Calling):**
```json
{
  "id": "chatcmpl-llama4-weather-001",
  "object": "chat.completion", 
  "created": 1642694800,
  "model": "ai-agent-llama4-scout",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "The current temperature in London, United Kingdom is 18°C. The weather conditions are partly cloudy with light winds from the southwest at 15 km/h. Humidity is at 65% and visibility is good at 10 km."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 42,
    "total_tokens": 67
  },
  "metadata": {
    "agent_type": "weather",
    "model_backend": "llama4:scout", 
    "tool_calls_made": 1,
    "tools_used": ["get_weather"],
    "cities_queried": ["London"],
    "llama4_features": {
      "native_tool_calling": true,
      "context_preserved": true,
      "expert_networks_used": ["tool_calling", "weather_analysis"]
    },
    "processing_details": {
      "geocoding_time": "120ms",
      "weather_api_time": "340ms", 
      "llama4_processing_time": "680ms",
      "total_time": "1140ms"
    }
  }
}
```

### 4. Multi-City Weather Comparison (Advanced Tool Calling)

**Meta Llama 4 Scout can call multiple tools in parallel:**

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user", 
        "content": "Compare the weather in London, Tokyo, and New York right now. Which city has the best weather for outdoor activities?"
      }
    ],
    "temperature": 0.7,
    "max_tokens": 400
  }'
```

**Response (Multi-Tool calling):**
```json
{
  "id": "chatcmpl-llama4-multiweather-002",
  "object": "chat.completion",
  "created": 1642694800,
  "model": "ai-agent-llama4-scout",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant", 
      "content": "Here's the current weather comparison for the three cities:\n\n🌤️ **London, UK**: 18°C, partly cloudy, light winds (15 km/h), humidity 65%\n🌸 **Tokyo, Japan**: 25°C, clear skies, gentle breeze (8 km/h), humidity 45%  \n☁️ **New York, USA**: 22°C, overcast, moderate winds (20 km/h), humidity 70%\n\n**Best for outdoor activities**: **Tokyo** is currently the winner! With clear skies, pleasant 25°C temperature, low humidity, and gentle winds, it's perfect for outdoor activities. \n\n**Second place**: New York has good temperature but overcast skies.\n**Third place**: London is cooler and more humid, though still suitable for most activities.\n\nTokyo's clear sunny conditions make it ideal for hiking, sports, or any outdoor plans today!"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 58,
    "completion_tokens": 165,
    "total_tokens": 223
  },
  "metadata": {
    "agent_type": "weather",
    "model_backend": "llama4:scout",
    "tool_calls_made": 3,
    "tools_used": ["get_weather", "get_weather", "get_weather"],
    "cities_queried": ["London", "Tokyo", "New York"],
    "llama4_features": {
      "parallel_tool_calling": true,
      "comparative_analysis": true,
      "context_synthesis": true,
      "expert_networks_used": ["tool_calling", "weather_analysis", "reasoning", "comparison"]
    },
    "processing_details": {
      "parallel_geocoding": "150ms",
      "parallel_weather_apis": "420ms",
      "llama4_synthesis": "890ms", 
      "total_time": "1460ms"
    }
  }
}
```

### 5. Legacy Model (Llama 3.x fallback)

**For systems using legacy models without native tool calling:**

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is the temperature in Paris?"}
    ],
    "temperature": 0.7
  }'
```

**Response (Legacy processing):**
```json
{
  "id": "chatcmpl-legacy-003", 
  "object": "chat.completion",
  "created": 1642694800,
  "model": "ai-agent-legacy-llama3",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "The current temperature in Paris, France is 22°C. Weather conditions are sunny with light clouds."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 18,
    "total_tokens": 38
  },
  "metadata": {
    "agent_type": "weather",
    "model_backend": "llama3.1:8b-instruct-q4_0",
    "processing_mode": "legacy",
    "tool_calls_made": 1,
    "llama_version": "3.x",
    "enhanced_features": false
  }
}
```

## Open WebUI Examples with Meta Llama 4 Scout

### Accessing the web interface

1. **Start the full stack**:
   ```bash
   ./start-webui.sh
   ```

2. **Open browser**: Navigate to `http://localhost:3000`

3. **Login/Create Account**: 
   - Email: test@example.com (can be fake for local)
   - Password: your-secure-password
   - Full Name: Test User

4. **Select Model**: Choose "ai-agent-llama4-scout" from dropdown

### Conversations in Open WebUI

#### **1. Testing Llama 4 Scout features**

**Open WebUI:**
```
Hello! I'm excited to try Meta Llama 4 Scout. Can you explain your advanced capabilities and how they differ from regular chatbots?
```

**AI Agent (Llama 4 Scout response):**
```
Hello! I'm thrilled to showcase my Meta Llama 4 Scout capabilities! I'm quite different from regular chatbots in several key ways:

🧠 **10 Million Token Context Window**
Unlike typical chatbots with 4K-8K token limits, I can maintain context across extremely long conversations. We could discuss a complex topic for hours, and I'll remember everything we've covered.

⚡ **Mixture of Experts Architecture** 
I use 8 specialized expert networks that activate based on your query type:
- Reasoning experts for logic problems
- Tool-calling experts for real-time data
- Conversation experts for natural dialogue
- Analysis experts for complex breakdowns

🛠️ **Native Tool Calling**
I can automatically detect when you need real-time information and call tools without you having to ask specifically. For example, if you mention weather, I'll fetch current data.

🎯 **Enhanced Reasoning**
I excel at multi-step logic, complex problem-solving, and analytical thinking that goes beyond simple pattern matching.

Try asking me about weather in multiple cities, give me a complex reasoning problem, or start a long technical discussion - I'll demonstrate these capabilities in action!
```

#### **2. Weather Tool Calling in action**

**You:**
```
I'm planning trips to London, Tokyo, and Sydney this month. What's the current weather like in each city, and which would be best for outdoor sightseeing today?
```

**AI Agent (with automatic tool calling):**
```
I'll check the current weather in all three cities for you right now!

*[Automatically calls weather tools for London, Tokyo, and Sydney]*

Here's the current weather comparison:

🌤️ **London, UK**
- Temperature: 18°C (64°F)
- Conditions: Partly cloudy
- Wind: 15 km/h SW
- Humidity: 65%

🌸 **Tokyo, Japan**  
- Temperature: 25°C (77°F)
- Conditions: Clear skies
- Wind: 8 km/h E
- Humidity: 45%

🌊 **Sydney, Australia**
- Temperature: 28°C (82°F)  
- Conditions: Sunny
- Wind: 12 km/h NE
- Humidity: 55%

**Best for outdoor sightseeing today**: **Sydney** takes the top spot! Perfect sunny weather at 28°C with low humidity makes it ideal for walking tours, harbor visits, or exploring the city.

**Second place**: Tokyo with its clear skies and pleasant 25°C temperature.

**Third place**: London is still nice but cooler and more humid - though perfect if you prefer milder temperatures!

All three cities have good conditions today, but Sydney's sunny warmth makes it perfect for outdoor adventures! 🌞
```

#### **3. Multi-turn conversation**

**You:**
```
Let's have a technical discussion. I'm working on a machine learning project involving time series forecasting. Can you explain the differences between LSTM, GRU, and Transformer models for this use case?
```

**AI Agent (First response):**
```
Excellent question! Time series forecasting is a fascinating application where model architecture choice significantly impacts performance. Let me break down these three approaches:

## LSTM (Long Short-Term Memory)

**Architecture**: Uses memory cells with three gates (forget, input, output) to control information flow.

**Strengths for Time Series**:
- Excellent at capturing long-term dependencies
- Handles vanishing gradient problem well
- Great for sequential patterns with irregular intervals
- Memory cells can selectively remember important historical events

**Best Use Cases**: Financial data, weather patterns, sales forecasting with seasonal trends

## GRU (Gated Recurrent Unit)

**Architecture**: Simplified version of LSTM with two gates (reset, update) - fewer parameters.

**Strengths for Time Series**:
- Faster training than LSTM (fewer parameters)
- Still captures long-term dependencies effectively
- Less prone to overfitting on smaller datasets
- Better computational efficiency

**Best Use Cases**: Resource-constrained environments, shorter sequences, real-time forecasting

## Transformers

**Architecture**: Attention-based mechanism without recurrence - processes sequences in parallel.

**Strengths for Time Series**:
- Excellent at capturing long-range dependencies
- Parallel processing enables faster training
- Self-attention reveals important time relationships
- Can handle very long sequences (like my 10M token context!)

**Best Use Cases**: Very long sequences, complex multi-variate time series, when you have substantial computational resources

What specific characteristics does your time series data have? Length, seasonality, noise level? I can provide more targeted recommendations based on your specific use case.
```

**You (Follow-up):**
```
My data is hourly energy consumption for a smart grid over 2 years, with strong daily and weekly patterns. I have about 17,000 data points. Which would you recommend and why?
```

**AI Agent (Contextual follow-up with full memory):**
```
Perfect! Based on your specific requirements - hourly energy consumption with 17K points and strong daily/weekly patterns - here's my recommendation:

## Recommended: **LSTM** (Primary choice)

**Why LSTM is ideal for your use case**:

1. **Pattern Recognition**: LSTMs excel at learning hierarchical patterns. Your data has:
   - Daily cycles (24-hour patterns)  
   - Weekly cycles (7-day patterns)
   - Seasonal variations (2-year span)
   
2. **Sequence Length**: 17K points is in LSTM's sweet spot - long enough to benefit from memory cells, not so long that you need Transformer's parallel processing.

3. **Energy Domain Fit**: Energy consumption has:
   - Clear temporal dependencies (past usage predicts future)
   - Event-driven spikes (holidays, weekends) that LSTMs remember well
   - Non-linear relationships that LSTM gates handle effectively

## Architecture Suggestions:

```python
# Recommended LSTM setup for your energy data
model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(lookback_window, 1)),
    Dropout(0.2),
    LSTM(50, return_sequences=False),
    Dropout(0.2),
    Dense(25),
    Dense(1)
])
```

**Hyperparameters for energy data**:
- Lookback window: 168 hours (1 week) to capture weekly patterns
- Batch size: 32-64 
- Learning rate: 0.001
- Epochs: 100-200 with early stopping

## Why not the others?

**GRU**: Would work but LSTM's explicit memory control is better for your multi-layered patterns (daily + weekly + seasonal).

**Transformer**: Overkill for 17K points, and energy consumption patterns are more sequential than attention-based relationships.

Would you like me to dive deeper into feature engineering for your smart grid data? Things like time-based features, holiday indicators, or weather correlations could significantly boost your model's performance!
```

#### **4. Advanced Reasoning Challenge**

**You:**
```
Here's a logic puzzle: You have 12 balls, one of which is different in weight (either heavier or lighter). You have a balance scale and can use it exactly 3 times to identify the different ball and determine if it's heavier or lighter. How do you solve this?
```

**AI Agent (Advanced reasoning):**
```
Excellent classic puzzle! This requires strategic thinking and process of elimination. Let me walk through the optimal solution:

## The solution: Strategic weighing

### **First weighing**
Divide the 12 balls into groups of 4:
- **Left pan**: Balls 1, 2, 3, 4
- **Right pan**: Balls 5, 6, 7, 8  
- **Set aside**: Balls 9, 10, 11, 12

### **Analysis after first weighing**

**Case A: Scale balances**
→ The different ball is among balls 9, 10, 11, 12

**Case B: Left side heavier**  
→ Either balls 1-4 contain a heavy ball, OR balls 5-8 contain a light ball

**Case C: Left side lighter**
→ Either balls 1-4 contain a light ball, OR balls 5-8 contain a heavy ball

### **Second weighing strategy**

**If Case A (balanced)**: 
- **Left pan**: Balls 9, 10
- **Right pan**: Balls 11, 1 (we know ball 1 is normal)

**If Case B (left heavier)**:
- **Left pan**: Balls 1, 2, 5
- **Right pan**: Balls 3, 6, 9 (ball 9 is normal)

**If Case C (left lighter)**:
- **Left pan**: Balls 1, 2, 6  
- **Right pan**: Balls 3, 5, 9 (ball 9 is normal)

### **Third weighing & identification**

The beauty is that after the second weighing, you'll have narrowed it down to 2-3 possible balls, and the third weighing will definitively identify both:
1. **Which ball is different**
2. **Whether it's heavier or lighter**

The key insight is using known normal balls as "controls" in subsequent weighings, and strategically mixing suspected heavy/light balls to isolate the variables.

Would you like me to work through the complete decision tree for any specific case? The logic branches beautifully into exactly 3 weighings every time! 🧠⚖️
```

### **5. Long Context Window Demonstration**

**You (Start of long conversation):**
```
I'm going to test your 10 million token context window. Please remember that I'm working on three projects: 1) A smart home system with IoT sensors, 2) A mobile app for fitness tracking, and 3) A machine learning model for energy forecasting. Throughout our conversation, I want you to remember these projects and reference them when relevant.

Now, let's start: What are the key considerations for sensor placement in IoT systems?
```

**AI Agent:**
```
I'll definitely remember your three projects throughout our entire conversation! Let me address sensor placement for your smart home IoT system specifically:

## Considerations for IoT sensor placement

### **1. Environmental factors**
- **Temperature/humidity sensors**: Avoid direct sunlight, heat sources, air vents
- **Motion sensors**: Corner placement for maximum room coverage
- **Air quality sensors**: Central locations, away from windows/doors

### **2. Network connectivity**
- Signal strength mapping throughout your home
- Consider mesh network topology for reliability  
- Plan for potential interference (WiFi, Bluetooth, microwave)

### **3. Power management**
- Battery-powered sensors: accessible locations for maintenance
- Wired sensors: near power outlets or plan conduit routing
- Solar sensors: south-facing windows with consistent light

### **4. Security**
- Camera sensors: visible placement for transparency
- Audio sensors: avoid bedrooms/private areas
- Secure mounting to prevent tampering

### **5. Smart home integration**
Since this is one of your three projects, consider how sensor data will integrate with your other work:
- Could sensor data inform your energy forecasting ML model?
- Environmental data might be useful for your fitness app's outdoor activity recommendations

### **6. Redundancy & reliability**
- Critical sensors (smoke, security): multiple units
- Backup power for essential safety sensors
- Weather-resistant housing for outdoor sensors

What specific types of sensors are you planning for your smart home system? I can provide more targeted placement strategies based on your sensor selection and home layout!

*[Remembering: Project 1: Smart home IoT sensors, Project 2: Fitness app, Project 3: Energy forecasting ML]*
```

**You (Much later in conversation):**
```
Going back to that energy forecasting project we discussed earlier - how could I integrate data from my smart home sensors to improve the model's accuracy?
```

**AI Agent (Demonstrating context retention):**
```
Excellent connection! I remember your energy forecasting ML model (Project 3) and your smart home IoT sensor system (Project 1). Integrating these could significantly boost your model's accuracy:

## Smart home sensor integration for energy forecasting

### **Direct energy correlations**

**Temperature & humidity sensors**:
- HVAC load prediction (heating/cooling demand)
- Seasonal adjustment factors
- Real-time comfort vs efficiency optimization

**Occupancy sensors (motion/door/window)**:
- Occupancy-based load forecasting
- Lighting and appliance usage patterns
- Vacation/away mode detection for baseline adjustment

**Light sensors**:
- Natural light availability → artificial lighting needs
- Solar generation potential (if you have panels)
- Circadian rhythm-based usage patterns

### **Feature Engineering**

Remember your hourly energy consumption data with 17K points? Adding sensor features:

```python
# Enhanced features from your IoT sensors
features = {
    'hour_of_day': original_time_features,
    'outdoor_temp': weather_data,  # Original
    'indoor_temp': smart_home_sensors,  # NEW
    'occupancy_count': motion_sensors,  # NEW  
    'door_openings': door_sensors,  # NEW
    'natural_light': light_sensors,  # NEW
    'humidity_indoor': humidity_sensors  # NEW
}
```

### **Multi-Modal learning**

You could create an ecosystem:
- **Energy model** predicts usage based on occupancy
- **Smart home** optimizes based on predictions  
- **Fitness app** could inform occupancy patterns (gym vs home workouts)

### **Implementation**

1. **Start basics**: Add indoor temperature and occupancy first
2. **Validate impacts**: Compare RMSE before/after sensor integration
3. **Expand gradually**: Add more sensor types based on correlation analysis

Your LSTM model architecture I recommended earlier can easily handle these additional input features - just expand the input dimension from `(lookback_window, 1)` to `(lookback_window, n_features)`.

This sensor integration could improve your energy forecasting accuracy by 15-30% based on similar smart grid studies!

*[Context maintained: All three projects integrated - IoT sensors, fitness app, energy forecasting]*
```

## Advanced testing scenarios

### **1. Testing script**

Create a complete test script `test_llama4_examples.sh`:

```bash
#!/bin/bash
echo "=== Meta Llama 4 Scout AI Agent Testing ==="
echo "Testing all capabilities: Health, Greetings, Weather, Advanced Reasoning"
echo

# Test 1: Health Check with Llama 4 metadata
echo "1. Testing Health Check (Llama 4 Scout Metadata)..."
health_response=$(curl -s http://localhost:8000/health)
echo "$health_response" | jq '.'
echo

# Test 2: Llama 4 Scout Capabilities Introduction
echo "2. Testing Llama 4 Scout Introduction..."
curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello! Please introduce yourself and explain your Meta Llama 4 Scout capabilities"}],
    "temperature": 0.7
  }' | jq '.choices[0].message.content'
echo

# Test 3: Single City Weather (Tool Calling)
echo "3. Testing Single City Weather Tool Calling..."
curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is the current temperature and weather conditions in Tokyo?"}],
    "temperature": 0.7
  }' | jq '.choices[0].message.content'
echo

# Test 4: Multi-City Weather Comparison (Advanced Tool Calling)
echo "4. Testing Multi-City Weather Comparison..."
curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Compare the weather in London, New York, and Sydney. Which city has the best conditions for outdoor activities right now?"}],
    "temperature": 0.7
  }' | jq '.choices[0].message.content'
echo

# Test 5: Complex Reasoning Challenge
echo "5. Testing Advanced Reasoning..."
curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Solve this logic puzzle: I have 8 coins, 7 real and 1 fake. The fake coin is lighter. Using a balance scale only twice, how can I identify the fake coin?"}],
    "temperature": 0.7,
    "max_tokens": 500
  }' | jq '.choices[0].message.content'
echo

# Test 6: Technical Discussion (Context Window Test)
echo "6. Testing Technical Discussion..."
curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Explain the trade-offs between microservices and monolithic architecture for a scalable web application. Consider performance, development complexity, and deployment."}],
    "temperature": 0.7,
    "max_tokens": 600
  }' | jq '.choices[0].message.content'
echo

echo "=== Testing Complete ==="
```

### **2. Open WebUI tests**

#### **Scenario A: Travel planning assistant**

**Test Conversation flow:**
1. **Initial request**: "I'm planning a European trip to London, Paris, Amsterdam, and Berlin in March. Help me understand the weather patterns and best activities for each city."

2. **Follow-up**: "Based on the current weather you showed me, which city should I visit first this week?"

3. **Planning**: "If I have 2 weeks total, how should I sequence these cities to take advantage of the best weather patterns?"

#### **Scenario B: Technical questions**

**Conversation flow:**
1. **Technical question**: "I'm building a distributed system with microservices. What are the key patterns for handling inter-service communication?"

2. **Follow-up**: "You mentioned message queues. Can you compare RabbitMQ, Apache Kafka, and Redis Pub/Sub for different use cases?"

3. **Implementation**: "For my specific case with 50,000 daily users and high availability requirements, which would you recommend and why?"

#### **Scenario C: Context window stress test**

**Long Conversation test:**
1. Start with: "I'm going to give you a complex scenario with many details. Remember everything for our entire conversation..."

2. Provide detailed information about multiple projects, requirements, constraints

3. Throughout the conversation, reference earlier details and expect Llama 4 Scout to maintain context

4. Test with 100+ exchanges to verify 10M token context window

### **3. Performance benchmarking**

#### **Response Time benchmarks**

```bash
#!/bin/bash
echo "=== Llama 4 Scout Performance Benchmarks ==="

# Simple greeting benchmark
echo "Testing simple greeting response time..."
time curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}' > /dev/null

# Weather tool calling benchmark
echo "Testing weather tool calling response time..."
time curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "What is the temperature in London?"}]}' > /dev/null

# Multi-city weather benchmark
echo "Testing multi-city weather response time..."
time curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Compare weather in London, Tokyo, New York, and Sydney"}]}' > /dev/null

# Complex reasoning benchmark
echo "Testing complex reasoning response time..."
time curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Explain quantum computing and its applications in cryptography"}]}' > /dev/null
```

#### **Performance metrics**

**Meta Llama 4 Scout (Recommended hardware)**:
- Simple greeting: 800ms - 1.2s
- Single weather query: 1.1s - 1.8s  
- Multi-city weather: 1.5s - 2.5s
- Complex reasoning: 2.0s - 3.5s

**Legacy Llama 3.x (Fallback)**:
- Simple greeting: 400ms - 800ms
- Weather query: 800ms - 1.2s
- Complex reasoning: 1.2s - 2.0s

### **4. Error handling**

#### **Invalid weather queries**

```bash
# Test invalid city name
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is the weather in Fakecityname123?"}]
  }'
```

**Expected behavior**: Graceful handling with suggestions for valid cities.

#### **API rate limiting**

```bash
# Test concurrent requests
for i in {1..10}; do
  curl -X POST http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"messages": [{"role": "user", "content": "Hello '$i'"}]}' &
done
wait
```

#### **Network connectivity issues**

```bash
# Test with offline weather API (simulate network issues)
sudo iptables -A OUTPUT -d api.open-meteo.com -j DROP
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "What is the weather in London?"}]}'
# Restore connectivity
sudo iptables -D OUTPUT -d api.open-meteo.com -j DROP
```

## Model comparison

### **Meta Llama 4 Scout vs Legacy models**

| Feature | Llama 4 Scout | Llama 3.1 8B | Llama 3.1 7B |
|---------|---------------|---------------|---------------|
| Context Window | 10M tokens | 4K tokens | 4K tokens |
| Tool Calling | Native | Prompt-based | Prompt-based |
| MoE Architecture | ✅ 8 experts | ❌ | ❌ |
| Response Quality | Excellent | Very Good | Good |
| Resource Usage | High | Medium | Low |
| Setup Complexity | Medium | Easy | Easy |

### **Use Cases**

#### **Choose Llama 4 Scout when:**
- Long conversations/documents (>4K tokens)
- Complex reasoning tasks
- Native tool calling needed
- Multi-step problem solving
- High-quality responses critical

#### **Choose Llama 3.x when:**
- Limited hardware resources
- Simple Q&A scenarios  
- Quick setup required
- Basic tool integration sufficient
- Cost optimization important

## Integration with agents.py and tools.py

### **Functions in agents.py**

The `agents.py` file provides OpenAI-compatible API endpoints:

```python
# Key function: OpenAI-compatible chat completion
async def process_chat_completion(self, messages: List[Dict[str, str]], 
                                temperature: float = 0.7, 
                                max_tokens: int = 512) -> Dict[str, Any]:
    """
    Process chat completion with Llama 4 Scout metadata.
    
    Returns enhanced response with:
    - Llama 4 feature information
    - Tool calling metadata  
    - Performance metrics
    - Expert network usage
    """
```

### **Functions in tools.py**

The `tools.py` file handles LLM integration and tool calling:

```python
# Model detection and prompt formatting
class LLMTool:
    def __init__(self, model: str = "llama4:scout"):
        self.is_llama4 = "llama4" in model.lower()
        self.context_size = 10000000 if self.is_llama4 else 4096
    
    def _create_llama4_prompt(self, user_message: str, system_message: str):
        """Create Llama 4 Scout native prompt format with tool definitions"""
    
    def _create_llama_legacy_prompt(self, user_message: str, system_message: str):
        """Create Llama 3.x compatible prompt format"""
    
    async def _handle_tool_calls(self, response_text: str, original_message: str):
        """Process Llama 4 Scout native tool calling responses"""
```

### **Tool integration**

#### **Adding new tools to Llama 4 Scout**

```python
# In tools.py - extend tool definitions
def _create_llama4_prompt(self, user_message: str, system_message: str, tools: List[Dict]):
    system_with_tools = f"""{system_message}

Available tools:
- get_weather(city, metric): Get current weather information
- calculate_math(expression): Perform mathematical calculations
- search_web(query): Search for recent information
- translate_text(text, target_language): Translate text to specified language

When using tools, respond with the format:
[tool_name(param1="value1", param2="value2")]
"""
    # ... rest of prompt formatting
```

These examples in the document provides everything needed to use and test Meta Llama 4 Scout with the AI Agent system.
```
```

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello, how are you today?"}
    ],
    "temperature": 0.7
  }'
```

**Response:**
```json
{
  "id": "chatcmpl-abc123...",
  "object": "chat.completion",
  "created": 1721376600,
  "model": "ai-agent-no-framework",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Hello! I'm doing great, thank you for asking. I'm here and ready to help you with any questions you might have, whether it's about weather information, general topics, or just having a friendly conversation. How can I assist you today?"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 6,
    "completion_tokens": 45,
    "total_tokens": 51
  },
  "metadata": {
    "agent_type": "greeting",
    "timestamp": "2025-07-19T10:30:00",
    "session_id": "abc123..."
  }
}
```

### 3. Weather query

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is the temperature in Tokyo?"}
    ]
  }'
```

**Response:**
```json
{
  "id": "chatcmpl-def456...",
  "object": "chat.completion",
  "created": 1721376700,
  "model": "ai-agent-no-framework",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "The current temperature in Tokyo, Japan is 28°C. Weather conditions: Partly cloudy"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 8,
    "completion_tokens": 15,
    "total_tokens": 23
  },
  "metadata": {
    "agent_type": "weather",
    "timestamp": "2025-07-19T10:31:40",
    "session_id": "abc123...",
    "city": "Tokyo"
  }
}
```

### 4. Use of LLM query

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Explain what artificial intelligence is in simple terms"}
    ],
    "temperature": 0.5
  }'
```

### 5. Use of weather endpoint

```bash
curl -X POST http://localhost:8000/v1/weather?city=London
```

**Response:**
```json
{
  "city": "London",
  "response": "The current temperature in London, United Kingdom is 18°C. Weather conditions: Overcast",
  "metadata": {
    "agent_type": "weather",
    "timestamp": "2025-07-19T10:32:00",
    "city": "London"
  }
}
```

## Python client examples

### Client script

```python
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"

def chat_with_agent(message, temperature=0.7):
    """Send a message to the AI agent."""
    url = f"{BASE_URL}/v1/chat/completions"
    payload = {
        "messages": [{"role": "user", "content": message}],
        "temperature": temperature
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.text}"

# Examples
print("Greeting:", chat_with_agent("Hello!"))
print("Weather:", chat_with_agent("What's the temperature in Paris?"))
print("General:", chat_with_agent("What is Python programming?"))
```

### Async client script

```python
import asyncio
import aiohttp
import json

async def async_chat_with_agent(session, message):
    """Async chat with the agent."""
    url = "http://localhost:8000/v1/chat/completions"
    payload = {
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.7
    }
    
    async with session.post(url, json=payload) as response:
        if response.status == 200:
            data = await response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status}"

async def main():
    async with aiohttp.ClientSession() as session:
        # Send multiple requests concurrently
        messages = [
            "Hello, how are you?",
            "What's the weather in Tokyo?",
            "Tell me about machine learning",
            "Good morning!"
        ]
        
        tasks = [async_chat_with_agent(session, msg) for msg in messages]
        responses = await asyncio.gather(*tasks)
        
        for msg, resp in zip(messages, responses):
            print(f"Q: {msg}")
            print(f"A: {resp[:100]}...")
            print("-" * 40)

# Run the async example
asyncio.run(main())
```

## JavaScript/Node.js examples

### Fetch

```javascript
async function chatWithAgent(message, temperature = 0.7) {
    const response = await fetch('http://localhost:8000/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            messages: [{ role: 'user', content: message }],
            temperature: temperature
        })
    });
    
    const data = await response.json();
    return data.choices[0].message.content;
}

// Usage
chatWithAgent('Hello!')
    .then(response => console.log('Response:', response))
    .catch(error => console.error('Error:', error));
```

### React component

```jsx
import React, { useState } from 'react';

function AIChat() {
    const [message, setMessage] = useState('');
    const [response, setResponse] = useState('');
    const [loading, setLoading] = useState(false);

    const sendMessage = async () => {
        setLoading(true);
        try {
            const res = await fetch('http://localhost:8000/v1/chat/completions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    messages: [{ role: 'user', content: message }]
                })
            });
            
            const data = await res.json();
            setResponse(data.choices[0].message.content);
        } catch (error) {
            setResponse('Error: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <input 
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Ask me anything..."
            />
            <button onClick={sendMessage} disabled={loading}>
                {loading ? 'Thinking...' : 'Send'}
            </button>
            <div>{response}</div>
        </div>
    );
}
```

## Testing and development

### Run component tests

```bash
# Test individual components without server
python test_components.py
```

### Run API tests

```bash
# Test API endpoints (server must be running)
./test_api.sh
```

### Development

```bash
# Start server with auto-reload
ENVIRONMENT=development python src/index.py
```

### Using Makefile commands

```bash
make help          # Show all available commands
make setup         # Full setup
make run           # Start server
make test          # Test components
make test-api      # Test API
make health        # Quick health check
make clean         # Clean up
```

## Customization

### Custom tool example

Add to `tools.py`:

```python
class CustomTool:
    async def process_custom_query(self, message: str) -> str:
        # Custom logic here
        return f"Processed: {message}"

# Add to ToolManager
async def process_message(self, message: str, temperature: float = 0.7):
    # Add custom condition
    if "custom:" in message.lower():
        custom_tool = CustomTool()
        response = await custom_tool.process_custom_query(message)
        return {
            "type": "custom",
            "content": response,
            "timestamp": datetime.now().isoformat()
        }
    # ... rest of existing logic
```

### Environment configuration

Create `.env` file:

```env
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama3.1:7b-instruct-q4_0
SERVER_HOST=127.0.0.1
SERVER_PORT=8080
ENVIRONMENT=production
```

## Monitoring and logging

### Health monitoring

```python
import requests
import time

def monitor_health():
    while True:
        try:
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                data = response.json()
                print(f"Status: {data['status']} - LLM: {data['services']['llm']}")
            else:
                print(f"Health check failed: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(30)  # Check every 30 seconds

monitor_health()
```

## Performance

1. **Concurrent requests**: The agent supports multiple concurrent requests
2. **Temperature settings**: Use lower temperatures (0.1-0.3) for factual queries, higher (0.7-1.0) for creative responses
3. **Model selection**: Use smaller models (7b) for faster responses, larger (8b) for better quality
4. **Caching**: Implement caching for weather data to reduce API calls
5. **Connection pooling**: Use session management for multiple requests

## Troubleshooting

### Issues

1. **Ollama connection**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # Restart Ollama
   ollama serve
   ```

2. **Model not found**
   ```bash
   # List available models
   ollama list
   
   # Pull the model
   ollama pull llama3.1:8b-instruct-q4_0
   ```

3. **Weather API**
   - Open-Meteo doesn't require API keys
   - Check internet connection
   - Try different city names

4. **Port already in use**
   ```bash
   # Change port in .env file
   SERVER_PORT=8001
   ```
