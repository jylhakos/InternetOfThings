package com.example.springaidemo.controller;

import com.example.springaidemo.model.ChatRequest;
import com.example.springaidemo.model.ChatResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.QuestionAnswerAdvisor;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

/**
 * REST Controller for RAG-based chat interactions
 * Uses ChatClient with QuestionAnswerAdvisor for retrieval-augmented generation
 */
@RestController
@RequestMapping("/api/chat")
public class ChatController {

    private static final Logger logger = LoggerFactory.getLogger(ChatController.class);

    private final ChatClient chatClient;
    private final VectorStore vectorStore;
    
    @Value("${spring.ai.ollama.chat.options.model:llama3.2}")
    private String modelName;

    public ChatController(ChatClient.Builder chatClientBuilder, VectorStore vectorStore) {
        this.vectorStore = vectorStore;
        
        // Build ChatClient with default RAG advisor
        this.chatClient = chatClientBuilder
                .defaultAdvisors(
                        QuestionAnswerAdvisor.builder(vectorStore)
                                .searchRequest(SearchRequest.builder()
                                        .similarityThreshold(0.7)
                                        .topK(5)
                                        .build())
                                .build()
                )
                .build();
    }

    /**
     * Simple chat endpoint with RAG
     * Example: POST /api/chat/ask?question=What is Spring AI?
     */
    @PostMapping("/ask")
    public ChatResponse ask(@RequestParam String question) {
        logger.info("Received question: {}", question);
        
        long startTime = System.currentTimeMillis();
        
        String answer = chatClient.prompt()
                .user(question)
                .call()
                .content();
        
        long responseTime = System.currentTimeMillis() - startTime;
        
        logger.info("Generated answer in {}ms", responseTime);
        
        return new ChatResponse(answer, List.of(), responseTime, modelName);
    }

    /**
     * Advanced chat endpoint with customizable RAG parameters
     * Example: POST /api/chat
     * Body: {"question": "What is Spring AI?", "similarityThreshold": 0.8, "topK": 3}
     */
    @PostMapping
    public ChatResponse chat(@RequestBody ChatRequest request) {
        logger.info("Received chat request: {}", request);
        
        long startTime = System.currentTimeMillis();
        
        String answer;
        
        if (request.isIncludeContext()) {
            // Use RAG with custom similarity threshold and topK
            answer = chatClient.prompt()
                    .user(request.getQuestion())
                    .advisors(advisor -> advisor
                            .advisors(QuestionAnswerAdvisor.builder(vectorStore)
                                    .searchRequest(SearchRequest.builder()
                                            .similarityThreshold(request.getSimilarityThreshold())
                                            .topK(request.getTopK())
                                            .build())
                                    .build())
                    )
                    .call()
                    .content();
        } else {
            // Direct query without RAG
            answer = chatClient.prompt()
                    .user(request.getQuestion())
                    .advisors(advisor -> advisor.advisors()) // Clear advisors
                    .call()
                    .content();
        }
        
        long responseTime = System.currentTimeMillis() - startTime;
        
        logger.info("Generated answer in {}ms", responseTime);
        
        // Get relevant document sources
        List<String> sources = getRelevantSources(request.getQuestion(), 
                request.getSimilarityThreshold(), 
                request.getTopK());
        
        return new ChatResponse(answer, sources, responseTime, modelName);
    }

    /**
     * Stream chat endpoint for real-time responses
     * Example: GET /api/chat/stream?question=What is Spring AI?
     */
    @GetMapping(value = "/stream", produces = "text/event-stream")
    public String streamChat(@RequestParam String question) {
        logger.info("Received streaming question: {}", question);
        
        // Note: For proper streaming, you would use Spring WebFlux
        // This is a simplified example
        return chatClient.prompt()
                .user(question)
                .call()
                .content();
    }

    /**
     * Get relevant document sources for a question
     */
    private List<String> getRelevantSources(String question, double threshold, int topK) {
        try {
            var documents = vectorStore.similaritySearch(
                    SearchRequest.builder()
                            .query(question)
                            .similarityThreshold(threshold)
                            .topK(topK)
                            .build()
            );
            
            return documents.stream()
                    .map(doc -> (String) doc.getMetadata().get("source"))
                    .distinct()
                    .collect(Collectors.toList());
        } catch (Exception e) {
            logger.error("Error retrieving sources", e);
            return List.of();
        }
    }

    /**
     * Health check endpoint
     */
    @GetMapping("/health")
    public String health() {
        return "Chat service is running with model: " + modelName;
    }
}
