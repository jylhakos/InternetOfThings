package com.llm.serving.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * Configuration properties for LLM settings
 */
@Component
@ConfigurationProperties(prefix = "llm")
public class LlmProperties {
    
    private System system = new System();
    private int maxTokens = 2048;
    private long timeout = 30000;
    
    public System getSystem() {
        return system;
    }
    
    public void setSystem(System system) {
        this.system = system;
    }
    
    public int getMaxTokens() {
        return maxTokens;
    }
    
    public void setMaxTokens(int maxTokens) {
        this.maxTokens = maxTokens;
    }
    
    public long getTimeout() {
        return timeout;
    }
    
    public void setTimeout(long timeout) {
        this.timeout = timeout;
    }
    
    public static class System {
        private String template = "You are a helpful assistant.";
        
        public String getTemplate() {
            return template;
        }
        
        public void setTemplate(String template) {
            this.template = template;
        }
    }
}
