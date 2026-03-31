package com.example.springaidemo.config;

import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.ai.vectorstore.qdrant.QdrantVectorStore;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Configuration for Vector Store
 * This example uses Qdrant as the vector database
 */
@Configuration
public class VectorStoreConfig {

    /**
     * The VectorStore bean is auto-configured by Spring Boot
     * based on the dependencies and properties in application.yml
     * 
     * This configuration class is kept for documentation purposes
     * and can be used to customize the VectorStore if needed
     */
    
    // Example of manual VectorStore configuration (if auto-configuration is not sufficient)
    /*
    @Bean
    public VectorStore vectorStore(EmbeddingModel embeddingModel) {
        return QdrantVectorStore.builder()
            .embeddingModel(embeddingModel)
            .host("localhost")
            .port(6334)
            .collectionName("spring-ai-documentation")
            .build();
    }
    */
}
