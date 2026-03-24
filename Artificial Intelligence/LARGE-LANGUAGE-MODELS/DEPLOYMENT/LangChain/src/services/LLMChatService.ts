import {
  START,
  END,
  StateGraph,
  MemorySaver,
  MessagesAnnotation,
  Annotation,
} from '@langchain/langgraph';
import { ChatPromptTemplate } from '@langchain/core/prompts';
import { trimMessages } from '@langchain/core/messages';
import { HumanMessage, AIMessage, SystemMessage } from '@langchain/core/messages';
import { v4 as uuidv4 } from 'uuid';
import { logger } from '../utils/logger';

// For local/open-source LLM integration
import { ChatOpenAI } from '@langchain/openai';

interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface ChatCompletionRequest {
  messages: ChatMessage[];
  model?: string;
  temperature?: number;
  maxTokens?: number;
  stream?: boolean;
  userId?: string;
}

interface ChatCompletionResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: Array<{
    index: number;
    message: ChatMessage;
    finish_reason: string;
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

// Define the graph state annotation
const GraphAnnotation = Annotation.Root({
  ...MessagesAnnotation.spec,
  language: Annotation<string>(),
  userId: Annotation<string>(),
  temperature: Annotation<number>(),
});

export class LLMChatService {
  private llm: ChatOpenAI;
  private app: any;
  private memory: MemorySaver;
  private promptTemplate: ChatPromptTemplate;
  private trimmer: any;
  private isInitialized = false;

  constructor() {
    this.memory = new MemorySaver();
    this.initializePromptTemplate();
    this.initializeMessageTrimmer();
  }

  private initializePromptTemplate(): void {
    this.promptTemplate = ChatPromptTemplate.fromMessages([
      [
        'system',
        `You are a helpful AI assistant powered by Meta Llama-3.1. 
        You provide accurate, helpful, and safe responses to user questions.
        You respond in {language} when specified, otherwise in English.
        Be concise but thorough in your responses.
        If you're unsure about something, say so rather than making up information.`
      ],
      ['placeholder', '{messages}']
    ]);
  }

  private initializeMessageTrimmer(): void {
    this.trimmer = trimMessages({
      maxTokens: parseInt(process.env.LLM_MAX_TOKENS || '4096') * 0.8, // Reserve 20% for response
      strategy: 'last',
      tokenCounter: (msgs: any[]) => msgs.length * 50, // Rough estimate
      includeSystem: true,
      allowPartial: false,
      startOn: 'human',
    });
  }

  public async initialize(): Promise<void> {
    try {
      // Initialize the LLM model
      // This can be configured to use different models:
      // 1. OpenAI API (for testing/fallback)
      // 2. Local Llama model via Ollama
      // 3. HuggingFace Inference API
      // 4. Custom local inference server

      if (process.env.OPENAI_API_KEY) {
        // Use OpenAI API (can be configured to point to local inference server)
        this.llm = new ChatOpenAI({
          openAIApiKey: process.env.OPENAI_API_KEY,
          modelName: process.env.LLM_MODEL_NAME || 'gpt-3.5-turbo',
          temperature: parseFloat(process.env.LLM_TEMPERATURE || '0.7'),
          maxTokens: parseInt(process.env.LLM_MAX_TOKENS || '4096'),
          configuration: {
            baseURL: process.env.OPENAI_BASE_URL || 'https://api.openai.com/v1',
          },
        });
      } else if (process.env.HUGGINGFACE_API_KEY) {
        // Use HuggingFace Inference API for Llama models
        logger.info('Using HuggingFace Inference API for Llama model');
        this.llm = new ChatOpenAI({
          openAIApiKey: process.env.HUGGINGFACE_API_KEY,
          modelName: process.env.LLM_MODEL_NAME || 'meta-llama/Llama-3.1-8B-Instruct',
          temperature: parseFloat(process.env.LLM_TEMPERATURE || '0.7'),
          maxTokens: parseInt(process.env.LLM_MAX_TOKENS || '4096'),
          configuration: {
            baseURL: process.env.HUGGINGFACE_MODEL_ENDPOINT,
          },
        });
      } else {
        throw new Error('No LLM configuration found. Please set OPENAI_API_KEY or HUGGINGFACE_API_KEY');
      }

      await this.createChatApplication();
      this.isInitialized = true;
      logger.info('✅ LLM Chat Service initialized successfully');
    } catch (error) {
      logger.error('❌ Failed to initialize LLM Chat Service:', error);
      throw error;
    }
  }

  private async createChatApplication(): Promise<void> {
    // Define the function that calls the model
    const callModel = async (state: typeof GraphAnnotation.State) => {
      try {
        // Trim messages to fit context window
        const trimmedMessages = await this.trimmer.invoke(state.messages);
        
        // Prepare prompt with trimmed messages
        const prompt = await this.promptTemplate.invoke({
          messages: trimmedMessages,
          language: state.language || 'English',
        });

        // Call the LLM
        const response = await this.llm.invoke(prompt);
        
        // Return the response message
        return { messages: [response] };
      } catch (error) {
        logger.error('Error in model call:', error);
        throw error;
      }
    };

    // Create the state graph
    const workflow = new StateGraph(GraphAnnotation)
      .addNode('model', callModel)
      .addEdge(START, 'model')
      .addEdge('model', END);

    // Compile the application with memory
    this.app = workflow.compile({ checkpointer: this.memory });
  }

  public async generateChatCompletion(request: ChatCompletionRequest): Promise<ChatCompletionResponse> {
    if (!this.isInitialized) {
      throw new Error('LLM Chat Service not initialized');
    }

    try {
      const threadId = request.userId ? `user_${request.userId}` : uuidv4();
      const config = { configurable: { thread_id: threadId } };

      // Convert OpenAI format messages to LangChain format
      const messages = request.messages.map(msg => {
        switch (msg.role) {
          case 'system':
            return new SystemMessage(msg.content);
          case 'user':
            return new HumanMessage(msg.content);
          case 'assistant':
            return new AIMessage(msg.content);
          default:
            return new HumanMessage(msg.content);
        }
      });

      // Prepare the input
      const input = {
        messages: [messages[messages.length - 1]], // Only send the latest message
        language: 'English',
        userId: request.userId || 'anonymous',
        temperature: request.temperature || parseFloat(process.env.LLM_TEMPERATURE || '0.7'),
      };

      // Invoke the chat application
      const output = await this.app.invoke(input, config);
      const lastMessage = output.messages[output.messages.length - 1];

      // Format response in OpenAI compatible format
      const response: ChatCompletionResponse = {
        id: `chatcmpl-${uuidv4()}`,
        object: 'chat.completion',
        created: Math.floor(Date.now() / 1000),
        model: request.model || process.env.LLM_MODEL_NAME || 'meta-llama/Llama-3.1-8B-Instruct',
        choices: [
          {
            index: 0,
            message: {
              role: 'assistant',
              content: lastMessage.content,
            },
            finish_reason: 'stop',
          }
        ],
        usage: {
          prompt_tokens: lastMessage.usage_metadata?.input_tokens || 0,
          completion_tokens: lastMessage.usage_metadata?.output_tokens || 0,
          total_tokens: lastMessage.usage_metadata?.total_tokens || 0,
        }
      };

      logger.info('Chat completion generated successfully', {
        threadId,
        model: response.model,
        tokens: response.usage.total_tokens,
      });

      return response;
    } catch (error) {
      logger.error('Error generating chat completion:', error);
      throw error;
    }
  }

  public async getChatHistory(userId: string): Promise<ChatMessage[]> {
    try {
      const threadId = `user_${userId}`;
      const config = { configurable: { thread_id: threadId } };

      // Get the conversation state
      const state = await this.app.getState(config);
      
      if (!state || !state.values.messages) {
        return [];
      }

      // Convert LangChain messages to OpenAI format
      return state.values.messages.map((msg: any) => ({
        role: msg._getType() === 'human' ? 'user' : 'assistant',
        content: msg.content,
      }));
    } catch (error) {
      logger.error('Error getting chat history:', error);
      return [];
    }
  }

  public async clearChatHistory(userId: string): Promise<void> {
    try {
      const threadId = `user_${userId}`;
      const config = { configurable: { thread_id: threadId } };

      // Clear the conversation state
      await this.memory.delete(config);
      
      logger.info('Chat history cleared', { userId, threadId });
    } catch (error) {
      logger.error('Error clearing chat history:', error);
      throw error;
    }
  }

  public getModelInfo(): any {
    return {
      model: process.env.LLM_MODEL_NAME || 'meta-llama/Llama-3.1-8B-Instruct',
      maxTokens: parseInt(process.env.LLM_MAX_TOKENS || '4096'),
      temperature: parseFloat(process.env.LLM_TEMPERATURE || '0.7'),
      quantized: process.env.USE_QUANTIZED_MODEL === 'true',
      memoryOptimized: true,
      supportedFeatures: [
        'chat_completion',
        'conversation_history',
        'message_trimming',
        'multi_language',
        'streaming' // Future implementation
      ]
    };
  }
}
