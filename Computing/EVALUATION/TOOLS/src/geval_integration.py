#!/usr/bin/env python3
"""
G-Eval Integration for BERT Model Evaluation
Implements G-Eval methodology using LLM-as-a-judge with chain-of-thoughts
"""

import os
import json
import time
from typing import List, Dict, Optional, Tuple
import openai
from dataclasses import dataclass

@dataclass
class GEvalCriteria:
    """G-Eval evaluation criteria definition"""
    name: str
    description: str
    scale: str
    prompt_template: str

class GEvaluator:
    """
    G-Eval implementation using LLM-as-a-judge methodology
    Based on the paper: "G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment"
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize G-Evaluator
        
        Args:
            api_key: OpenAI API key (if None, reads from environment)
            model: LLM model to use for evaluation
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
        if not self.api_key:
            print("⚠️  Warning: No OpenAI API key provided. G-Eval will not work.")
            print("Set OPENAI_API_KEY environment variable or pass api_key parameter.")
            self.client = None
        else:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
                print(f"✅ G-Evaluator initialized with model: {model}")
            except Exception as e:
                print(f"❌ Failed to initialize OpenAI client: {e}")
                self.client = None
        
        self.criteria = self._define_evaluation_criteria()
    
    def _define_evaluation_criteria(self) -> Dict[str, GEvalCriteria]:
        """Define evaluation criteria for BERT sentiment classification"""
        criteria = {}
        
        # Sentiment Accuracy
        criteria["sentiment_accuracy"] = GEvalCriteria(
            name="Sentiment Accuracy",
            description="How accurately does the prediction match the true sentiment of the text?",
            scale="1-5 (1=completely wrong, 5=perfectly accurate)",
            prompt_template="""
You are an expert evaluator assessing sentiment classification accuracy.

Task: Evaluate how accurately the predicted sentiment matches the true sentiment of the given text.

Evaluation Criteria:
- 5: Perfect match - prediction exactly captures the sentiment expressed in the text
- 4: Very good - prediction captures the main sentiment with minor nuances missed
- 3: Good - prediction captures the general sentiment direction but misses some subtleties
- 2: Poor - prediction captures some sentiment but misses the main emotional tone
- 1: Very poor - prediction completely misses or contradicts the text's sentiment

Text: "{text}"
True Sentiment: {true_label}
Predicted Sentiment: {prediction}

Please provide your evaluation step by step:
1. Analyze the emotional tone and sentiment expressed in the text
2. Compare the true sentiment with the predicted sentiment
3. Consider the confidence and appropriateness of the prediction
4. Assign a score from 1-5 based on the criteria above

Score: [Your score]
Reasoning: [Your detailed reasoning]
"""
        )
        
        # Confidence Appropriateness
        criteria["confidence_appropriateness"] = GEvalCriteria(
            name="Confidence Appropriateness",
            description="How appropriate is the model's confidence level for this prediction?",
            scale="1-5 (1=very inappropriate, 5=very appropriate)",
            prompt_template="""
You are an expert evaluator assessing the appropriateness of model confidence.

Task: Evaluate whether the model's confidence level is appropriate for the given prediction.

Evaluation Criteria:
- 5: Confidence perfectly matches prediction quality (high confidence for clear cases, low for ambiguous)
- 4: Confidence is very appropriate with minor calibration issues
- 3: Confidence is generally appropriate but could be better calibrated
- 2: Confidence is somewhat inappropriate (too high/low for the prediction quality)
- 1: Confidence is very inappropriate (overconfident on wrong predictions or underconfident on clear cases)

Text: "{text}"
Predicted Sentiment: {prediction}
Model Confidence: {confidence:.3f}
True Sentiment: {true_label}

Please provide your evaluation step by step:
1. Assess the clarity/ambiguity of the text's sentiment
2. Evaluate the correctness of the prediction
3. Determine if the confidence level matches the prediction difficulty and accuracy
4. Assign a score from 1-5 based on the criteria above

Score: [Your score]
Reasoning: [Your detailed reasoning]
"""
        )
        
        # Robustness
        criteria["robustness"] = GEvalCriteria(
            name="Robustness",
            description="How robust is the prediction to text variations and edge cases?",
            scale="1-5 (1=very fragile, 5=very robust)",
            prompt_template="""
You are an expert evaluator assessing model robustness.

Task: Evaluate how robust the sentiment prediction is likely to be for similar texts.

Evaluation Criteria:
- 5: Prediction shows strong understanding of sentiment cues, likely robust to variations
- 4: Prediction demonstrates good sentiment understanding with minor robustness concerns
- 3: Prediction is reasonable but may struggle with similar edge cases
- 2: Prediction shows limited understanding, likely fragile to text variations
- 1: Prediction appears fragile and unreliable for similar texts

Text: "{text}"
Predicted Sentiment: {prediction}
True Sentiment: {true_label}

Please provide your evaluation step by step:
1. Identify key sentiment indicators in the text
2. Assess whether the prediction relies on robust sentiment features
3. Consider how the prediction might perform on similar or modified texts
4. Assign a score from 1-5 based on the criteria above

Score: [Your score]
Reasoning: [Your detailed reasoning]
"""
        )
        
        return criteria
    
    def evaluate_single(self, text: str, prediction: str, true_label: str, 
                       confidence: float, criterion: str) -> Dict:
        """
        Evaluate a single prediction using G-Eval methodology
        
        Args:
            text: Input text
            prediction: Model prediction
            true_label: True label
            confidence: Model confidence score
            criterion: Evaluation criterion to use
            
        Returns:
            Dictionary with evaluation results
        """
        if not self.client:
            return {"error": "OpenAI client not initialized"}
        
        if criterion not in self.criteria:
            return {"error": f"Unknown criterion: {criterion}"}
        
        criteria_obj = self.criteria[criterion]
        
        # Format the prompt
        prompt = criteria_obj.prompt_template.format(
            text=text,
            prediction=prediction,
            true_label=true_label,
            confidence=confidence
        )
        
        try:
            # Call LLM for evaluation
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert AI model evaluator. Provide detailed, objective assessments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent evaluation
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content
            
            # Parse score from response (basic parsing - could be improved)
            score = self._extract_score(result_text)
            reasoning = self._extract_reasoning(result_text)
            
            return {
                "criterion": criterion,
                "score": score,
                "reasoning": reasoning,
                "full_response": result_text,
                "model_used": self.model
            }
            
        except Exception as e:
            return {"error": f"Evaluation failed: {str(e)}"}
    
    def evaluate_batch(self, texts: List[str], predictions: List[str], 
                      true_labels: List[str], confidences: List[float],
                      criteria: Optional[List[str]] = None) -> Dict:
        """
        Evaluate a batch of predictions using G-Eval
        
        Args:
            texts: List of input texts
            predictions: List of model predictions
            true_labels: List of true labels
            confidences: List of confidence scores
            criteria: List of criteria to evaluate (if None, uses all)
            
        Returns:
            Dictionary with batch evaluation results
        """
        if not self.client:
            return {"error": "OpenAI client not initialized"}
        
        if criteria is None:
            criteria = list(self.criteria.keys())
        
        print(f"🔍 Running G-Eval on {len(texts)} samples with {len(criteria)} criteria...")
        
        results = {
            "summary": {},
            "individual_results": [],
            "criteria_used": criteria,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Track scores for each criterion
        criterion_scores = {c: [] for c in criteria}
        
        # Evaluate each sample
        for i, (text, pred, true_label, conf) in enumerate(zip(texts, predictions, true_labels, confidences)):
            print(f"Evaluating sample {i+1}/{len(texts)}...")
            
            sample_results = {
                "sample_id": i,
                "text": text,
                "prediction": pred,
                "true_label": true_label,
                "confidence": conf,
                "evaluations": {}
            }
            
            # Evaluate with each criterion
            for criterion in criteria:
                eval_result = self.evaluate_single(text, pred, true_label, conf, criterion)
                sample_results["evaluations"][criterion] = eval_result
                
                if "score" in eval_result and eval_result["score"] is not None:
                    criterion_scores[criterion].append(eval_result["score"])
            
            results["individual_results"].append(sample_results)
            
            # Add small delay to avoid rate limiting
            time.sleep(0.5)
        
        # Calculate summary statistics
        for criterion in criteria:
            scores = criterion_scores[criterion]
            if scores:
                results["summary"][criterion] = {
                    "mean_score": sum(scores) / len(scores),
                    "min_score": min(scores),
                    "max_score": max(scores),
                    "num_evaluated": len(scores),
                    "criterion_description": self.criteria[criterion].description
                }
        
        return results
    
    def _extract_score(self, response_text: str) -> Optional[int]:
        """Extract numerical score from LLM response"""
        import re
        
        # Look for "Score: X" pattern
        score_match = re.search(r'Score:\s*(\d+)', response_text, re.IGNORECASE)
        if score_match:
            return int(score_match.group(1))
        
        # Look for standalone numbers 1-5
        numbers = re.findall(r'\b([1-5])\b', response_text)
        if numbers:
            return int(numbers[0])  # Return first valid score found
        
        return None
    
    def _extract_reasoning(self, response_text: str) -> str:
        """Extract reasoning from LLM response"""
        import re
        
        # Look for "Reasoning: ..." pattern
        reasoning_match = re.search(r'Reasoning:\s*(.+)', response_text, re.IGNORECASE | re.DOTALL)
        if reasoning_match:
            return reasoning_match.group(1).strip()
        
        # If no explicit reasoning section, return the full response
        return response_text.strip()
    
    def save_results(self, results: Dict, filename: Optional[str] = None):
        """Save G-Eval results to JSON file"""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"geval_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 G-Eval results saved to: {filename}")
    
    def print_summary(self, results: Dict):
        """Print G-Eval results summary"""
        print("\n" + "="*60)
        print("🔍 G-EVAL RESULTS SUMMARY")
        print("="*60)
        
        if "error" in results:
            print(f"❌ Error: {results['error']}")
            return
        
        summary = results.get("summary", {})
        
        for criterion, stats in summary.items():
            print(f"\n📊 {criterion.replace('_', ' ').title()}:")
            print(f"   Mean Score: {stats['mean_score']:.2f}/5")
            print(f"   Range: {stats['min_score']}-{stats['max_score']}")
            print(f"   Samples: {stats['num_evaluated']}")
            print(f"   Description: {stats['criterion_description']}")
        
        total_samples = len(results.get("individual_results", []))
        criteria_count = len(results.get("criteria_used", []))
        print(f"\n📈 Overall Statistics:")
        print(f"   Total Samples Evaluated: {total_samples}")
        print(f"   Criteria Used: {criteria_count}")
        print(f"   Model: {results.get('model_used', 'Unknown')}")


def demo_geval():
    """Demonstrate G-Eval usage"""
    
    # Sample data
    texts = [
        "I absolutely love this product! It exceeded my expectations.",
        "This is the worst service I've ever experienced.",
        "The movie was okay, nothing special but not terrible either."
    ]
    predictions = ["positive", "negative", "neutral"]
    true_labels = ["positive", "negative", "neutral"]
    confidences = [0.95, 0.89, 0.62]
    
    # Initialize G-Evaluator
    evaluator = GEvaluator()
    
    if not evaluator.client:
        print("❌ Cannot run G-Eval demo without OpenAI API key")
        print("Set OPENAI_API_KEY environment variable to use G-Eval")
        return
    
    # Run evaluation
    results = evaluator.evaluate_batch(
        texts=texts,
        predictions=predictions,
        true_labels=true_labels,
        confidences=confidences,
        criteria=["sentiment_accuracy", "confidence_appropriateness"]
    )
    
    # Print results
    evaluator.print_summary(results)
    
    # Save results
    evaluator.save_results(results)
    
    return results


if __name__ == "__main__":
    demo_geval()
