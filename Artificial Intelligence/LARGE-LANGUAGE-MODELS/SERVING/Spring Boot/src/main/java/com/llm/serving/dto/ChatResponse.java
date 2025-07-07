package com.llm.serving.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.LocalDateTime;

/**
 * Response DTO for chat messages
 */
public class ChatResponse {
    
    private String response;
    
    @JsonProperty("model_used")
    private String modelUsed;
    
    @JsonProperty("tokens_used")
    private Integer tokensUsed;
    
    @JsonProperty("response_time_ms")
    private Long responseTimeMs;
    
    private LocalDateTime timestamp;
    
    private boolean success = true;
    
    @JsonProperty("error_message")
    private String errorMessage;
    
    public ChatResponse() {
        this.timestamp = LocalDateTime.now();
    }
    
    public ChatResponse(String response) {
        this();
        this.response = response;
    }
    
    public static ChatResponse success(String response, String model, Integer tokens, Long responseTime) {
        ChatResponse chatResponse = new ChatResponse(response);
        chatResponse.setModelUsed(model);
        chatResponse.setTokensUsed(tokens);
        chatResponse.setResponseTimeMs(responseTime);
        return chatResponse;
    }
    
    public static ChatResponse error(String errorMessage) {
        ChatResponse chatResponse = new ChatResponse();
        chatResponse.setSuccess(false);
        chatResponse.setErrorMessage(errorMessage);
        return chatResponse;
    }
    
    public String getResponse() {
        return response;
    }
    
    public void setResponse(String response) {
        this.response = response;
    }
    
    public String getModelUsed() {
        return modelUsed;
    }
    
    public void setModelUsed(String modelUsed) {
        this.modelUsed = modelUsed;
    }
    
    public Integer getTokensUsed() {
        return tokensUsed;
    }
    
    public void setTokensUsed(Integer tokensUsed) {
        this.tokensUsed = tokensUsed;
    }
    
    public Long getResponseTimeMs() {
        return responseTimeMs;
    }
    
    public void setResponseTimeMs(Long responseTimeMs) {
        this.responseTimeMs = responseTimeMs;
    }
    
    public LocalDateTime getTimestamp() {
        return timestamp;
    }
    
    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }
    
    public boolean isSuccess() {
        return success;
    }
    
    public void setSuccess(boolean success) {
        this.success = success;
    }
    
    public String getErrorMessage() {
        return errorMessage;
    }
    
    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }
    
    @Override
    public String toString() {
        return "ChatResponse{" +
                "response='" + response + '\'' +
                ", modelUsed='" + modelUsed + '\'' +
                ", tokensUsed=" + tokensUsed +
                ", responseTimeMs=" + responseTimeMs +
                ", timestamp=" + timestamp +
                ", success=" + success +
                ", errorMessage='" + errorMessage + '\'' +
                '}';
    }
}
