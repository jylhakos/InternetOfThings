package com.llm.serving;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

/**
 * Main application class for Chat Service (LLMs)
 * Spring Boot application that serves Large Language Models through Ollama
 */
@SpringBootApplication
@ConfigurationPropertiesScan
public class LlmChatServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(LlmChatServiceApplication.class, args);
    }
}
