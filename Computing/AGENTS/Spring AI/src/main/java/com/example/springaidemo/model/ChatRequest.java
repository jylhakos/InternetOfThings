package com.example.springaidemo.model;

/**
 * Request model for chat queries
 */
public class ChatRequest {
    private String question;
    private boolean includeContext;
    private Double similarityThreshold;
    private Integer topK;

    public ChatRequest() {
        this.includeContext = true;
        this.similarityThreshold = 0.7;
        this.topK = 5;
    }

    public ChatRequest(String question) {
        this();
        this.question = question;
    }

    public String getQuestion() {
        return question;
    }

    public void setQuestion(String question) {
        this.question = question;
    }

    public boolean isIncludeContext() {
        return includeContext;
    }

    public void setIncludeContext(boolean includeContext) {
        this.includeContext = includeContext;
    }

    public Double getSimilarityThreshold() {
        return similarityThreshold;
    }

    public void setSimilarityThreshold(Double similarityThreshold) {
        this.similarityThreshold = similarityThreshold;
    }

    public Integer getTopK() {
        return topK;
    }

    public void setTopK(Integer topK) {
        this.topK = topK;
    }

    @Override
    public String toString() {
        return "ChatRequest{" +
                "question='" + question + '\'' +
                ", includeContext=" + includeContext +
                ", similarityThreshold=" + similarityThreshold +
                ", topK=" + topK +
                '}';
    }
}
