package com.llm.serving;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;

@SpringBootTest
@TestPropertySource(properties = {
    "spring.ai.ollama.base-url=http://localhost:11434"
})
class LlmChatServiceApplicationTests {

    @Test
    void contextLoads() {
        // Test that the Spring context loads successfully
    }
}
