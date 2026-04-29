"""
Batch Evaluation Script for AI Agents

This script runs comprehensive evaluations on AI agents using benchmark datasets
and logs all results to Langfuse for analysis.
"""

import os
import json
import argparse
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

from datasets import load_dataset
from langfuse import Langfuse

from agent_evaluation import run_agent_with_tracing, evaluate_agent_on_dataset

# Load environment variables
load_dotenv()


def load_hotpot_qa_dataset(num_samples: int = 10) -> List[Dict]:
    """
    Load HotpotQA dataset from Hugging Face.
    
    Args:
        num_samples: Number of samples to load
    
    Returns:
        List of test cases with input and expected output
    """
    print(f"Loading HotpotQA dataset ({num_samples} samples)...")
    
    try:
        # Load dataset from Hugging Face
        dataset = load_dataset("hotpot_qa", "distractor", split=f"validation[:{num_samples}]")
        
        # Convert to test case format
        test_cases = []
        for item in dataset:
            test_cases.append({
                "input": item["question"],
                "expected_output": item["answer"],
                "context": item.get("context", ""),
                "type": item.get("type", "unknown")
            })
        
        print(f"✓ Loaded {len(test_cases)} test cases from HotpotQA")
        return test_cases
        
    except Exception as e:
        print(f"✗ Error loading HotpotQA dataset: {str(e)}")
        print("  Using fallback dataset...")
        return get_fallback_dataset()


def get_fallback_dataset() -> List[Dict]:
    """
    Fallback dataset if HuggingFace dataset cannot be loaded.
    
    Returns:
        List of test cases
    """
    return [
        {
            "input": "What is the capital of France?",
            "expected_output": "Paris",
            "type": "factual"
        },
        {
            "input": "Who wrote Romeo and Juliet?",
            "expected_output": "William Shakespeare",
            "type": "factual"
        },
        {
            "input": "What is 144 divided by 12?",
            "expected_output": "12",
            "type": "mathematical"
        },
        {
            "input": "What is the speed of light in meters per second?",
            "expected_output": "299,792,458",
            "type": "factual"
        },
        {
            "input": "What is 25 multiplied by 8?",
            "expected_output": "200",
            "type": "mathematical"
        },
    ]


def create_langfuse_dataset(test_cases: List[Dict], dataset_name: str):
    """
    Create or update a dataset in Langfuse.
    
    Args:
        test_cases: List of test cases
        dataset_name: Name of the dataset in Langfuse
    """
    print(f"\nCreating/updating Langfuse dataset: {dataset_name}")
    
    langfuse = Langfuse()
    
    try:
        # Create dataset
        langfuse.create_dataset(name=dataset_name)
        print(f"✓ Dataset '{dataset_name}' created")
    except Exception as e:
        print(f"  Dataset may already exist: {str(e)}")
    
    # Add items to dataset
    for idx, test_case in enumerate(test_cases):
        try:
            langfuse.create_dataset_item(
                dataset_name=dataset_name,
                input={"question": test_case["input"]},
                expected_output={"answer": test_case["expected_output"]},
                metadata={
                    "type": test_case.get("type", "unknown"),
                    "index": idx
                }
            )
        except Exception as e:
            print(f"  Error adding item {idx}: {str(e)}")
    
    print(f"✓ Added {len(test_cases)} items to dataset")


def calculate_metrics(results: List[Dict]) -> Dict:
    """
    Calculate evaluation metrics from results.
    
    Args:
        results: List of evaluation results
    
    Returns:
        Dictionary of metrics
    """
    total = len(results)
    if total == 0:
        return {}
    
    correct = sum(1 for r in results if r.get("correct"))
    accuracy = correct / total
    
    # Calculate by type if available
    by_type = {}
    for result in results:
        test_type = result.get("type", "unknown")
        if test_type not in by_type:
            by_type[test_type] = {"total": 0, "correct": 0}
        
        by_type[test_type]["total"] += 1
        if result.get("correct"):
            by_type[test_type]["correct"] += 1
    
    # Calculate accuracy by type
    type_accuracy = {}
    for test_type, counts in by_type.items():
        type_accuracy[test_type] = counts["correct"] / counts["total"]
    
    return {
        "total_cases": total,
        "correct": correct,
        "accuracy": accuracy,
        "by_type": type_accuracy
    }


def save_results(results: List[Dict], metrics: Dict, output_file: str):
    """
    Save evaluation results to JSON file.
    
    Args:
        results: Evaluation results
        metrics: Calculated metrics
        output_file: Path to output file
    """
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics,
        "results": results
    }
    
    # Create results directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n✓ Results saved to: {output_file}")


def main():
    """Main execution function."""
    
    parser = argparse.ArgumentParser(description="Run batch evaluation on AI agent")
    parser.add_argument(
        "--dataset",
        type=str,
        default="fallback",
        choices=["hotpot_qa", "fallback"],
        help="Dataset to use for evaluation"
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        default=10,
        help="Number of samples to evaluate"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/evaluation_report.json",
        help="Output file for results"
    )
    parser.add_argument(
        "--create-langfuse-dataset",
        action="store_true",
        help="Create dataset in Langfuse"
    )
    
    args = parser.parse_args()
    
    print("="*70)
    print("AI Agent Batch Evaluation")
    print("="*70)
    print(f"Dataset: {args.dataset}")
    print(f"Samples: {args.num_samples}")
    print(f"Output: {args.output}")
    print("="*70)
    
    # Load dataset
    if args.dataset == "hotpot_qa":
        test_cases = load_hotpot_qa_dataset(args.num_samples)
    else:
        test_cases = get_fallback_dataset()[:args.num_samples]
    
    # Optionally create Langfuse dataset
    if args.create_langfuse_dataset:
        dataset_name = f"agent_eval_{args.dataset}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        create_langfuse_dataset(test_cases, dataset_name)
    
    # Run evaluation
    print("\nRunning evaluation...")
    results = evaluate_agent_on_dataset(
        test_cases=test_cases,
        dataset_name=f"batch_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    
    # Add type information to results
    for i, result in enumerate(results):
        if i < len(test_cases):
            result["type"] = test_cases[i].get("type", "unknown")
    
    # Calculate metrics
    metrics = calculate_metrics(results)
    
    # Print summary
    print("\n" + "="*70)
    print("Evaluation Summary")
    print("="*70)
    print(f"Total Test Cases: {metrics['total_cases']}")
    print(f"Correct: {metrics['correct']}")
    print(f"Accuracy: {metrics['accuracy']:.2%}")
    
    if metrics.get('by_type'):
        print("\nAccuracy by Type:")
        for test_type, accuracy in metrics['by_type'].items():
            print(f"  {test_type}: {accuracy:.2%}")
    
    # Save results
    save_results(results, metrics, args.output)
    
    print("\n✓ Evaluation complete!")
    print(f"✓ View detailed traces in Langfuse: {os.getenv('LANGFUSE_HOST', 'http://localhost:3000')}")


if __name__ == "__main__":
    # Check required environment variables
    required_vars = ["OPENAI_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"✗ Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("✗ Please create a .env file with the required variables")
        exit(1)
    
    main()
