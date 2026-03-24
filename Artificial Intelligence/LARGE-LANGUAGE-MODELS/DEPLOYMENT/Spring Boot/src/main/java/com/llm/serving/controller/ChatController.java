package com.llm.serving.controller;

import com.llm.serving.dto.ChatRequest;
import com.llm.serving.dto.ChatResponse;
import com.llm.serving.service.LlmChatService;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * REST Controller for LLM Chat API
 */
@RestController
@RequestMapping("/api/v1/chat")
@CrossOrigin(origins = "*", maxAge = 3600)
public class ChatController {
    
    private static final Logger logger = LoggerFactory.getLogger(ChatController.class);
    
    private final LlmChatService llmChatService;
    
    public ChatController(LlmChatService llmChatService) {
        this.llmChatService = llmChatService;
    }
    
    /**
     * Process chat message and return LLM response
     */
    @PostMapping
    public ResponseEntity<ChatResponse> chat(@Valid @RequestBody ChatRequest request) {
        logger.info("Received chat request");
        
        try {
            ChatResponse response = llmChatService.processChat(request);
            
            if (response.isSuccess()) {
                logger.info("Chat processed successfully in {}ms", response.getResponseTimeMs());
                return ResponseEntity.ok(response);
            } else {
                logger.error("Chat processing failed: {}", response.getErrorMessage());
                return ResponseEntity.badRequest().body(response);
            }
            
        } catch (Exception e) {
            logger.error("Unexpected error processing chat", e);
            ChatResponse errorResponse = ChatResponse.error("Internal server error: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResponse);
        }
    }
    
    /**
     * Simple health check endpoint
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        boolean ollamaHealthy = llmChatService.isOllamaHealthy();
        
        Map<String, Object> health = Map.of(
            "status", ollamaHealthy ? "UP" : "DOWN",
            "ollama", ollamaHealthy ? "HEALTHY" : "UNHEALTHY",
            "timestamp", System.currentTimeMillis()
        );
        
        if (ollamaHealthy) {
            return ResponseEntity.ok(health);
        } else {
            return ResponseEntity.status(503).body(health);
        }
    }
    
    /**
     * Get service information
     */
    @GetMapping("/info")
    public ResponseEntity<Map<String, String>> info() {
        Map<String, String> info = Map.of(
            "service", "LLM Chat Service",
            "version", "1.0.0",
            "model", "llama3",
            "provider", "Ollama"
        );
        
        return ResponseEntity.ok(info);
    }
}
