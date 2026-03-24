package com.llm.serving.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * Request DTO for chat messages
 */
public class ChatRequest {
    
    @NotBlank(message = "Message cannot be blank")
    @Size(max = 4000, message = "Message cannot exceed 4000 characters")
    private String message;
    
    @JsonProperty("use_system_template")
    private boolean useSystemTemplate = true;
    
    private Double temperature;
    private Double topP;
    private Integer maxTokens;
    
    public ChatRequest() {}
    
    public ChatRequest(String message) {
        this.message = message;
    }
    
    public String getMessage() {
        return message;
    }
    
    public void setMessage(String message) {
        this.message = message;
    }
    
    public boolean isUseSystemTemplate() {
        return useSystemTemplate;
    }
    
    public void setUseSystemTemplate(boolean useSystemTemplate) {
        this.useSystemTemplate = useSystemTemplate;
    }
    
    public Double getTemperature() {
        return temperature;
    }
    
    public void setTemperature(Double temperature) {
        this.temperature = temperature;
    }
    
    public Double getTopP() {
        return topP;
    }
    
    public void setTopP(Double topP) {
        this.topP = topP;
    }
    
    public Integer getMaxTokens() {
        return maxTokens;
    }
    
    public void setMaxTokens(Integer maxTokens) {
        this.maxTokens = maxTokens;
    }
    
    @Override
    public String toString() {
        return "ChatRequest{" +
                "message='" + message + '\'' +
                ", useSystemTemplate=" + useSystemTemplate +
                ", temperature=" + temperature +
                ", topP=" + topP +
                ", maxTokens=" + maxTokens +
                '}';
    }
}
