# Quick Start - Taxi Booking Agents by LangGraph

##  Getting Started

```bash
# 1. Navigate to the project
cd "src/JavaScript"

# 2. Install dependencies
npm install

# 3. Run the demo (works without API keys)
npm run demo

# 4. Run tests
npm test

# 5. Set up environment (optional - for full agent functionality)
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Commands

| Command | Description |
|---------|-------------|
| `npm run demo` | Interactive tool demonstration |
| `npm test` | Comprehensive test suite |
| `npm start` | Main agent application (requires OpenAI key) |
| `npm run dev` | Start LangGraph development server |
| `npm run sdk-example` | LangGraph SDK integration examples |
| `npm run setup` | Automated setup and validation |

## 🛠️ Components

### Tools (`tools/taxi-booking-tool.js`)
- **geocodingTool** - Convert city names to coordinates
- **bookTaxi** - Book taxi reservations
- **checkTaxiStatus** - Monitor booking status

### Agent (`agents/taxi-booking-agent.js`)
- LangGraph StateGraph implementation
- Tool binding and execution
- Conversation memory management

### Testing (`test/test-taxi-tool.js`)
- Comprehensive tool validation
- Error handling verification
- Schema compliance checks

## Features

**Cities**: London, Berlin, Paris, Madrid, Rome
**Taxi Types**: Economy, Premium, Luxury, Van
**Passengers**: 1-8 people per booking
**Status Tracking**: Real-time booking updates

## 🔧 Usage

```javascript
// Direct tool usage
import { taxiBookingTool } from './tools/taxi-booking-tool.js';

const booking = await taxiBookingTool.invoke({
  city: "London",
  pickup_address: "Heathrow Airport", 
  destination_address: "Westminster",
  passenger_count: 2,
  taxi_type: "economy"
});
```
**Add OpenAI API Key** - Enable full agent conversations

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraphjs/)
- [Tool Calling Guide](https://js.langchain.com/docs/concepts/tool_calling/)
- [Geocoding API](https://docs.maptiler.com/server/api/geocoding/)
