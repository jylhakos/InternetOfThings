const { PromptTemplate } = require("langchain/prompts");

/**
 * Default chat prompt template
 */
const DEFAULT_CHAT_TEMPLATE = new PromptTemplate({
  template: `You are a helpful AI assistant. Please provide a clear, informative, and helpful response to the user's question.

Question: {question}

Answer:`,
  inputVariables: ["question"]
});

/**
 * Conversation prompt template with context
 */
const CONVERSATION_TEMPLATE = new PromptTemplate({
  template: `You are a helpful AI assistant engaged in a conversation. Use the conversation history for context, but focus on answering the current question.

Conversation History:
{history}

Current Question: {question}

Answer:`,
  inputVariables: ["history", "question"]
});

/**
 * Code generation prompt template
 */
const CODE_TEMPLATE = new PromptTemplate({
  template: `You are an expert programmer. Generate clean, well-documented code based on the user's request.

Programming Language: {language}
Request: {request}

Please provide:
1. Clean, working code
2. Brief explanation of the solution
3. Any important notes or considerations

Code:`,
  inputVariables: ["language", "request"]
});

/**
 * Explanation prompt template
 */
const EXPLANATION_TEMPLATE = new PromptTemplate({
  template: `You are an expert educator. Explain the following topic in a clear, structured way that's easy to understand.

Topic: {topic}
Detail Level: {level}

Please provide:
1. Clear definition/overview
2. Key concepts and components
3. Practical examples when relevant
4. Summary of main points

Explanation:`,
  inputVariables: ["topic", "level"]
});

/**
 * Analysis prompt template
 */
const ANALYSIS_TEMPLATE = new PromptTemplate({
  template: `You are an expert analyst. Analyze the following content and provide insights.

Content to Analyze: {content}
Analysis Type: {type}

Please provide:
1. Key findings
2. Patterns or trends identified
3. Implications or recommendations
4. Summary of insights

Analysis:`,
  inputVariables: ["content", "type"]
});

/**
 * Creative writing prompt template
 */
const CREATIVE_TEMPLATE = new PromptTemplate({
  template: `You are a creative writer. Create engaging content based on the following prompt.

Genre/Style: {genre}
Prompt: {prompt}
Length: {length}

Please create content that is:
1. Engaging and well-written
2. Appropriate for the specified genre/style
3. Roughly the requested length
4. Creative and original

Content:`,
  inputVariables: ["genre", "prompt", "length"]
});

/**
 * Get appropriate prompt template based on request type
 */
function getPromptTemplate(type = 'default') {
  switch (type.toLowerCase()) {
    case 'conversation':
      return CONVERSATION_TEMPLATE;
    case 'code':
      return CODE_TEMPLATE;
    case 'explanation':
      return EXPLANATION_TEMPLATE;
    case 'analysis':
      return ANALYSIS_TEMPLATE;
    case 'creative':
      return CREATIVE_TEMPLATE;
    default:
      return DEFAULT_CHAT_TEMPLATE;
  }
}

/**
 * Format prompt with template
 */
async function formatPrompt(templateType, variables) {
  try {
    const template = getPromptTemplate(templateType);
    return await template.format(variables);
  } catch (error) {
    console.error('Error formatting prompt:', error);
    // Fallback to simple formatting
    if (variables.question) {
      return variables.question;
    }
    return variables.prompt || variables.content || "Please provide a helpful response.";
  }
}

module.exports = {
  DEFAULT_CHAT_TEMPLATE,
  CONVERSATION_TEMPLATE,
  CODE_TEMPLATE,
  EXPLANATION_TEMPLATE,
  ANALYSIS_TEMPLATE,
  CREATIVE_TEMPLATE,
  getPromptTemplate,
  formatPrompt
};
