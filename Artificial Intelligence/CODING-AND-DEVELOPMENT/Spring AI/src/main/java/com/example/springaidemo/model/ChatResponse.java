package com.example.springaidemo.model;

import java.util.List;

/**
 * Response model for chat queries
 */
public class ChatResponse {
    private String answer;
    private List<String> sources;
    private long responseTimeMs;
    private String model;

    public ChatResponse() {
    }

    public ChatResponse(String answer, List<String> sources, long responseTimeMs, String model) {
        this.answer = answer;
        this.sources = sources;
        this.responseTimeMs = responseTimeMs;
        this.model = model;
    }

    public String getAnswer() {
        return answer;
    }

    public void setAnswer(String answer) {
        this.answer = answer;
    }

    public List<String> getSources() {
        return sources;
    }

    public void setSources(List<String> sources) {
        this.sources = sources;
    }

    public long getResponseTimeMs() {
        return responseTimeMs;
    }

    public void setResponseTimeMs(long responseTimeMs) {
        this.responseTimeMs = responseTimeMs;
    }

    public String getModel() {
        return model;
    }

    public void setModel(String model) {
        this.model = model;
    }

    @Override
    public String toString() {
        return "ChatResponse{" +
                "answer='" + answer + '\'' +
                ", sources=" + sources +
                ", responseTimeMs=" + responseTimeMs +
                ", model='" + model + '\'' +
                '}';
    }
}
