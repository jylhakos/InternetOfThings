package com.llm.serving.service;

import com.llm.serving.config.LlmProperties;
import com.llm.serving.dto.ChatRequest;
import com.llm.serving.dto.ChatResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.ChatClient;
import org.springframework.ai.chat.messages.Message;
import org.springframework.ai.chat.messages.SystemMessage;
import org.springframework.ai.chat.messages.UserMessage;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.ollama.OllamaChatClient;
import org.springframework.ai.ollama.api.OllamaOptions;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

/**
 * Service for handling LLM chat operations through Ollama
 */
@Service
public class LlmChatService {
    
    private static final Logger logger = LoggerFactory.getLogger(LlmChatService.class);
    
    private final ChatClient chatClient;
    private final LlmProperties llmProperties;
    
    public LlmChatService(OllamaChatClient chatClient, LlmProperties llmProperties) {
        this.chatClient = chatClient;
        this.llmProperties = llmProperties;
    }
    
    /**
     * Process chat request and return response from LLM
     */
    public ChatResponse processChat(ChatRequest request) {
        logger.debug("Processing chat request: {}", request);
        
        long startTime = System.currentTimeMillis();
        
        try {
            // Build messages list
            List<Message> messages = new ArrayList<>();
            
            // Add system message if requested
            if (request.isUseSystemTemplate()) {
                messages.add(new SystemMessage(llmProperties.getSystem().getTemplate()));
            }
            
            // Add user message
            messages.add(new UserMessage(request.getMessage()));
            
            // Create prompt with messages
            Prompt prompt = new Prompt(messages, buildOllamaOptions(request));
            
            // Call Ollama
            org.springframework.ai.chat.ChatResponse response = chatClient.call(prompt);
            
            long responseTime = System.currentTimeMillis() - startTime;
            
            // Extract response content
            String responseText = response.getResult().getOutput().getContent();
            
            // Get metadata if available
            String modelUsed = extractModelFromMetadata(response);
            Integer tokensUsed = extractTokensFromMetadata(response);
            
            logger.debug("LLM response received in {}ms", responseTime);
            
            return ChatResponse.success(responseText, modelUsed, tokensUsed, responseTime);
            
        } catch (Exception e) {
            long responseTime = System.currentTimeMillis() - startTime;
            logger.error("Error processing chat request: ", e);
            
            ChatResponse errorResponse = ChatResponse.error("Failed to process request: " + e.getMessage());
            errorResponse.setResponseTimeMs(responseTime);
            return errorResponse;
        }
    }
    
    /**
     * Build Ollama options from request parameters
     */
    private OllamaOptions buildOllamaOptions(ChatRequest request) {
        OllamaOptions options = OllamaOptions.create();
        
        if (request.getTemperature() != null) {
            options = options.withTemperature(request.getTemperature().floatValue());
        }
        
        if (request.getTopP() != null) {
            options = options.withTopP(request.getTopP().floatValue());
        }
        
        if (request.getMaxTokens() != null) {
            options = options.withNumPredict(request.getMaxTokens());
        } else {
            options = options.withNumPredict(llmProperties.getMaxTokens());
        }
        
        return options;
    }
    
    /**
     * Extract model information from response metadata
     */
    private String extractModelFromMetadata(org.springframework.ai.chat.ChatResponse response) {
        try {
            return response.getMetadata().getModel();
        } catch (Exception e) {
            logger.debug("Could not extract model from metadata", e);
            return "llama3";
        }
    }
    
    /**
     * Extract token usage from response metadata
     */
    private Integer extractTokensFromMetadata(org.springframework.ai.chat.ChatResponse response) {
        try {
            return response.getMetadata().getUsage().getTotalTokens().intValue();
        } catch (Exception e) {
            logger.debug("Could not extract tokens from metadata", e);
            return null;
        }
    }
    
    /**
     * Health check for Ollama service
     */
    public boolean isOllamaHealthy() {
        try {
            Prompt testPrompt = new Prompt("Hello");
            chatClient.call(testPrompt);
            return true;
        } catch (Exception e) {
            logger.warn("Ollama health check failed: {}", e.getMessage());
            return false;
        }
    }
}
