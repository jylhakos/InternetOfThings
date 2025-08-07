import { ChatOllama } from "@langchain/ollama";
import { StateGraph, START, END } from "@langchain/langgraph";
import { ToolNode } from "@langchain/langgraph/prebuilt";
import { HumanMessage, AIMessage, ToolMessage } from "@langchain/core/messages";
import { taxiTools } from "../tools/taxi-booking-tool.js";
import * as dotenv from "dotenv";

// Load environment variables
dotenv.config();

/**
 * Define the state of our agent
 */
const AgentState = {
  messages: {
    value: (x, y) => x.concat(y),
    default: () => [],
  },
};

/**
 * OllamaTaxiBookingAgent - A LangGraph agent using local Ollama LLMs
 */
export class OllamaTaxiBookingAgent {
  constructor(options = {}) {
    this.model = new ChatOllama({
      baseUrl: options.baseUrl || process.env.OLLAMA_BASE_URL || "http://localhost:11434",
      model: options.model || process.env.OLLAMA_MODEL || "llama3.1:8b",
      temperature: options.temperature || 0.1,
      numCtx: 4096, // Context window
    });

    // Bind tools to the model
    this.modelWithTools = this.model.bindTools(taxiTools);
    
    // Create tool node for executing tools
    this.toolNode = new ToolNode(taxiTools);
    
    // Build the graph
    this.workflow = this.buildWorkflow();
    this.app = this.workflow.compile();
  }

  /**
   * Build the LangGraph workflow
   */
  buildWorkflow() {
    const workflow = new StateGraph(AgentState);

    // Add nodes
    workflow.addNode("agent", this.callModel.bind(this));
    workflow.addNode("tools", this.toolNode);

    // Set entry point
    workflow.setEntryPoint("agent");

    // Add conditional edges
    workflow.addConditionalEdges(
      "agent",
      this.shouldCallTool.bind(this),
      {
        tools: "tools",
        end: END,
      }
    );

    // Add edge from tools back to agent
    workflow.addEdge("tools", "agent");

    return workflow;
  }

  /**
   * Call the model with the current state
   */
  async callModel(state) {
    const messages = state.messages;
    const response = await this.modelWithTools.invoke(messages);
    return { messages: [response] };
  }

  /**
   * Determine whether to call tools or end
   */
  shouldCallTool(state) {
    const messages = state.messages;
    const lastMessage = messages[messages.length - 1];
    
    // If the last message has tool calls, we should call tools
    if (lastMessage.tool_calls && lastMessage.tool_calls.length > 0) {
      return "tools";
    }
    
    // Otherwise, we stop (this is the default)
    return "end";
  }

  /**
   * Process a user input and return the agent's response
   */
  async processMessage(userInput, config = {}) {
    try {
      const initialState = {
        messages: [new HumanMessage(userInput)]
      };

      let finalState;
      const stream = await this.app.stream(initialState, config);
      
      for await (const output of stream) {
        finalState = output;
      }

      // Extract the final response
      const messages = Object.values(finalState)[0].messages;
      const lastMessage = messages[messages.length - 1];
      
      return {
        success: true,
        response: lastMessage.content,
        toolCalls: this.extractToolCalls(messages),
        fullConversation: messages
      };
      
    } catch (error) {
      return {
        success: false,
        error: error.message,
        response: "Sorry, I encountered an error processing your request. Please make sure Ollama is running and the model is available."
      };
    }
  }

  /**
   * Extract tool calls from messages for debugging
   */
  extractToolCalls(messages) {
    const toolCalls = [];
    messages.forEach(message => {
      if (message.tool_calls && message.tool_calls.length > 0) {
        toolCalls.push(...message.tool_calls);
      }
    });
    return toolCalls;
  }

  /**
   * Stream responses from the agent
   */
  async streamResponse(userInput, config = {}) {
    const initialState = {
      messages: [new HumanMessage(userInput)]
    };

    const stream = this.app.stream(initialState, config);
    return stream;
  }

  /**
   * Get available tools information
   */
  getAvailableTools() {
    return taxiTools.map(tool => ({
      name: tool.name,
      description: tool.description,
      schema: tool.schema
    }));
  }

  /**
   * Test Ollama connection
   */
  async testConnection() {
    try {
      const response = await this.model.invoke([
        new HumanMessage("Hello, can you help me test the connection?")
      ]);
      return {
        success: true,
        response: response.content,
        model: this.model.model,
        baseUrl: this.model.baseUrl
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        suggestions: [
          "Make sure Ollama is running: ollama serve",
          `Install the model: ollama pull ${this.model.model}`,
          "Check if Ollama is accessible at: " + this.model.baseUrl
        ]
      };
    }
  }
}

/**
 * Create a pre-configured Ollama taxi booking agent
 */
export function createOllamaTaxiAgent(options = {}) {
  return new OllamaTaxiBookingAgent({
    baseUrl: options.baseUrl || process.env.OLLAMA_BASE_URL || "http://localhost:11434",
    model: options.model || process.env.OLLAMA_MODEL || "llama3.1:8b",
    temperature: options.temperature || 0.1,
    ...options
  });
}

/**
 * System prompt for the taxi booking agent (optimized for Ollama)
 */
export const OLLAMA_TAXI_AGENT_SYSTEM_PROMPT = `You are a helpful taxi booking assistant powered by Ollama. You can help users:

1. 🌍 Find locations using geocoding (get coordinates for cities)
2. 🚗 Book taxis in supported cities (London, Berlin, Paris, Madrid, Rome)  
3. 📊 Check the status of existing taxi bookings

When booking a taxi, gather all required information:
- City
- Pickup address/location
- Destination address/location  
- Number of passengers (1-8)
- Taxi type (economy, premium, luxury, van)
- Optional: specific booking time

Be friendly, efficient, and always confirm booking details before proceeding.
If a user asks about unsupported cities, explain which cities are currently supported.

Current supported cities: London, Berlin, Paris, Madrid, Rome

You are running locally using Ollama, which means responses stay private and secure.`;

export default OllamaTaxiBookingAgent;
