"""
LLM-as-a-Judge Evaluator

This module implements LLM-based evaluation for AI agent outputs,
providing quality scores for various dimensions like accuracy, relevance,
groundedness, and coherence.
"""

import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langfuse.decorators import observe

# Load environment variables
load_dotenv()


class LLMJudgeEvaluator:
    """
    LLM-as-a-Judge evaluator for AI agent outputs.
    """
    
    def __init__(self, model: str = "gpt-4", temperature: float = 0.0):
        """
        Initialize the evaluator.
        
        Args:
            model: OpenAI model to use for evaluation
            temperature: Temperature for generation (0 for deterministic)
        """
        self.llm = ChatOpenAI(model=model, temperature=temperature)
    
    @observe(name="evaluate_accuracy")
    def evaluate_accuracy(
        self,
        question: str,
        answer: str,
        expected_answer: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict:
        """
        Evaluate the accuracy of an answer.
        
        Args:
            question: The original question
            answer: The agent's answer
            expected_answer: The expected correct answer (optional)
            context: Additional context (optional)
        
        Returns:
            Dictionary with accuracy score and reasoning
        """
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert evaluator assessing the accuracy of AI responses.
Evaluate the answer based on factual correctness and completeness.

Provide your evaluation in the following JSON format:
{{
    "score": <0-100>,
    "reasoning": "<brief explanation>",
    "verdict": "<correct|partially_correct|incorrect>"
}}"""),
            ("user", """Question: {question}

Answer: {answer}
{expected_section}
{context_section}

Evaluate the accuracy of this answer.""")
        ])
        
        # Build optional sections
        expected_section = f"\nExpected Answer: {expected_answer}" if expected_answer else ""
        context_section = f"\nContext: {context}" if context else ""
        
        # Generate evaluation
        messages = prompt_template.format_messages(
            question=question,
            answer=answer,
            expected_section=expected_section,
            context_section=context_section
        )
        
        response = self.llm.invoke(messages)
        
        try:
            result = json.loads(response.content)
            return {
                "dimension": "accuracy",
                "score": result.get("score", 0) / 100.0,  # Normalize to 0-1
                "reasoning": result.get("reasoning", ""),
                "verdict": result.get("verdict", "unknown")
            }
        except json.JSONDecodeError:
            return {
                "dimension": "accuracy",
                "score": 0.0,
                "reasoning": "Failed to parse LLM response",
                "error": response.content
            }
    
    @observe(name="evaluate_relevance")
    def evaluate_relevance(self, question: str, answer: str) -> Dict:
        """
        Evaluate the relevance of an answer to the question.
        
        Args:
            question: The original question
            answer: The agent's answer
        
        Returns:
            Dictionary with relevance score and reasoning
        """
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert evaluator assessing answer relevance.
Evaluate how well the answer addresses the specific question asked.

Provide your evaluation in JSON format:
{{
    "score": <0-100>,
    "reasoning": "<brief explanation>",
    "verdict": "<highly_relevant|relevant|partially_relevant|not_relevant>"
}}"""),
            ("user", """Question: {question}

Answer: {answer}

Evaluate the relevance of this answer to the question.""")
        ])
        
        messages = prompt_template.format_messages(question=question, answer=answer)
        response = self.llm.invoke(messages)
        
        try:
            result = json.loads(response.content)
            return {
                "dimension": "relevance",
                "score": result.get("score", 0) / 100.0,
                "reasoning": result.get("reasoning", ""),
                "verdict": result.get("verdict", "unknown")
            }
        except json.JSONDecodeError:
            return {
                "dimension": "relevance",
                "score": 0.0,
                "reasoning": "Failed to parse LLM response",
                "error": response.content
            }
    
    @observe(name="evaluate_groundedness")
    def evaluate_groundedness(self, answer: str, context: str) -> Dict:
        """
        Evaluate if the answer is grounded in the provided context (for RAG systems).
        
        Args:
            answer: The agent's answer
            context: The source context/documents
        
        Returns:
            Dictionary with groundedness score and reasoning
        """
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert evaluator assessing answer groundedness.
Evaluate if the answer is fully supported by the provided context, or if it contains
information not present in the context (hallucinations).

Provide your evaluation in JSON format:
{{
    "score": <0-100>,
    "reasoning": "<brief explanation>",
    "verdict": "<fully_grounded|mostly_grounded|partially_grounded|not_grounded>",
    "hallucinations": "<list any unsupported claims>"
}}"""),
            ("user", """Context: {context}

Answer: {answer}

Evaluate if this answer is grounded in the context.""")
        ])
        
        messages = prompt_template.format_messages(context=context, answer=answer)
        response = self.llm.invoke(messages)
        
        try:
            result = json.loads(response.content)
            return {
                "dimension": "groundedness",
                "score": result.get("score", 0) / 100.0,
                "reasoning": result.get("reasoning", ""),
                "verdict": result.get("verdict", "unknown"),
                "hallucinations": result.get("hallucinations", "")
            }
        except json.JSONDecodeError:
            return {
                "dimension": "groundedness",
                "score": 0.0,
                "reasoning": "Failed to parse LLM response",
                "error": response.content
            }
    
    @observe(name="evaluate_coherence")
    def evaluate_coherence(self, answer: str) -> Dict:
        """
        Evaluate the coherence and logical consistency of an answer.
        
        Args:
            answer: The agent's answer
        
        Returns:
            Dictionary with coherence score and reasoning
        """
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert evaluator assessing answer coherence.
Evaluate the logical consistency, clarity, and organization of the answer.

Provide your evaluation in JSON format:
{{
    "score": <0-100>,
    "reasoning": "<brief explanation>",
    "verdict": "<highly_coherent|coherent|somewhat_coherent|incoherent>"
}}"""),
            ("user", """Answer: {answer}

Evaluate the coherence of this answer.""")
        ])
        
        messages = prompt_template.format_messages(answer=answer)
        response = self.llm.invoke(messages)
        
        try:
            result = json.loads(response.content)
            return {
                "dimension": "coherence",
                "score": result.get("score", 0) / 100.0,
                "reasoning": result.get("reasoning", ""),
                "verdict": result.get("verdict", "unknown")
            }
        except json.JSONDecodeError:
            return {
                "dimension": "coherence",
                "score": 0.0,
                "reasoning": "Failed to parse LLM response",
                "error": response.content
            }
    
    @observe(name="comprehensive_evaluation")
    def comprehensive_evaluation(
        self,
        question: str,
        answer: str,
        expected_answer: Optional[str] = None,
        context: Optional[str] = None,
        dimensions: Optional[List[str]] = None
    ) -> Dict:
        """
        Run comprehensive evaluation across multiple dimensions.
        
        Args:
            question: The original question
            answer: The agent's answer
            expected_answer: Expected correct answer (optional)
            context: Source context (optional)
            dimensions: List of dimensions to evaluate (default: all)
        
        Returns:
            Dictionary with all evaluation scores
        """
        
        if dimensions is None:
            dimensions = ["accuracy", "relevance", "coherence"]
            if context:
                dimensions.append("groundedness")
        
        results = {
            "question": question,
            "answer": answer,
            "evaluations": {}
        }
        
        # Run evaluations
        if "accuracy" in dimensions:
            results["evaluations"]["accuracy"] = self.evaluate_accuracy(
                question, answer, expected_answer, context
            )
        
        if "relevance" in dimensions:
            results["evaluations"]["relevance"] = self.evaluate_relevance(
                question, answer
            )
        
        if "groundedness" in dimensions and context:
            results["evaluations"]["groundedness"] = self.evaluate_groundedness(
                answer, context
            )
        
        if "coherence" in dimensions:
            results["evaluations"]["coherence"] = self.evaluate_coherence(answer)
        
        # Calculate average score
        scores = [
            eval_result["score"]
            for eval_result in results["evaluations"].values()
            if "score" in eval_result
        ]
        results["average_score"] = sum(scores) / len(scores) if scores else 0.0
        
        return results


# Example usage
def main():
    """Demo of LLM-as-a-Judge evaluation."""
    
    print("="*70)
    print("LLM-as-a-Judge Evaluation Demo")
    print("="*70)
    
    # Initialize evaluator
    evaluator = LLMJudgeEvaluator(model="gpt-3.5-turbo")
    
    # Example evaluation
    question = "What is the capital of France?"
    answer = "The capital of France is Paris, a beautiful city known for the Eiffel Tower."
    expected = "Paris"
    
    print(f"\nQuestion: {question}")
    print(f"Answer: {answer}")
    print(f"Expected: {expected}")
    
    # Run comprehensive evaluation
    results = evaluator.comprehensive_evaluation(
        question=question,
        answer=answer,
        expected_answer=expected
    )
    
    # Print results
    print("\n" + "-"*70)
    print("Evaluation Results")
    print("-"*70)
    print(f"Average Score: {results['average_score']:.2%}")
    
    for dimension, eval_result in results["evaluations"].items():
        print(f"\n{dimension.upper()}:")
        print(f"  Score: {eval_result['score']:.2%}")
        print(f"  Verdict: {eval_result['verdict']}")
        print(f"  Reasoning: {eval_result['reasoning']}")
    
    print("\n✓ Evaluation complete!")


if __name__ == "__main__":
    # Check required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("✗ Error: OPENAI_API_KEY environment variable not set")
        exit(1)
    
    main()
