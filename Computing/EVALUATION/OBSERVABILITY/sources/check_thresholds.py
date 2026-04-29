"""
Threshold Validation Script for CI/CD

This script checks evaluation results against quality thresholds and
fails the CI/CD pipeline if metrics don't meet requirements.
"""

import json
import argparse
import sys
from typing import Dict


def load_results(results_file: str) -> Dict:
    """
    Load evaluation results from JSON file.
    
    Args:
        results_file: Path to results JSON file
    
    Returns:
        Results dictionary
    """
    try:
        with open(results_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"✗ Error: Results file not found: {results_file}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"✗ Error: Invalid JSON in results file: {results_file}")
        sys.exit(1)


def check_threshold(metric_name: str, actual_value: float, threshold: float, minimum: bool = True) -> bool:
    """
    Check if a metric meets the threshold.
    
    Args:
        metric_name: Name of the metric
        actual_value: Actual metric value
        threshold: Threshold value
        minimum: If True, actual must be >= threshold. If False, actual must be <= threshold.
    
    Returns:
        True if threshold is met, False otherwise
    """
    if minimum:
        passed = actual_value >= threshold
        operator = ">="
    else:
        passed = actual_value <= threshold
        operator = "<="
    
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status} | {metric_name}: {actual_value:.3f} {operator} {threshold:.3f}")
    
    return passed


def validate_thresholds(results: Dict, thresholds: Dict) -> bool:
    """
    Validate all metrics against thresholds.
    
    Args:
        results: Evaluation results
        thresholds: Dictionary of threshold values
    
    Returns:
        True if all thresholds are met, False otherwise
    """
    metrics = results.get("metrics", {})
    
    print("\n" + "="*70)
    print("Threshold Validation")
    print("="*70)
    
    all_passed = True
    
    # Check accuracy threshold
    if "min_accuracy" in thresholds:
        accuracy = metrics.get("accuracy", 0.0)
        passed = check_threshold(
            "Overall Accuracy",
            accuracy,
            thresholds["min_accuracy"],
            minimum=True
        )
        all_passed = all_passed and passed
    
    # Check accuracy by type
    if "min_accuracy_by_type" in thresholds and "by_type" in metrics:
        for test_type, type_accuracy in metrics["by_type"].items():
            type_threshold = thresholds["min_accuracy_by_type"].get(test_type)
            if type_threshold is not None:
                passed = check_threshold(
                    f"  {test_type} Accuracy",
                    type_accuracy,
                    type_threshold,
                    minimum=True
                )
                all_passed = all_passed and passed
    
    # Check minimum correct count
    if "min_correct" in thresholds:
        correct = metrics.get("correct", 0)
        passed = check_threshold(
            "Correct Count",
            float(correct),
            float(thresholds["min_correct"]),
            minimum=True
        )
        all_passed = all_passed and passed
    
    # Check maximum error rate
    if "max_error_rate" in thresholds:
        total = metrics.get("total_cases", 1)
        errors = total - metrics.get("correct", 0)
        error_rate = errors / total if total > 0 else 1.0
        
        passed = check_threshold(
            "Error Rate",
            error_rate,
            thresholds["max_error_rate"],
            minimum=False
        )
        all_passed = all_passed and passed
    
    return all_passed


def print_summary(results: Dict):
    """
    Print evaluation summary.
    
    Args:
        results: Evaluation results
    """
    metrics = results.get("metrics", {})
    
    print("\n" + "="*70)
    print("Evaluation Summary")
    print("="*70)
    print(f"Timestamp: {results.get('timestamp', 'N/A')}")
    print(f"Total Cases: {metrics.get('total_cases', 0)}")
    print(f"Correct: {metrics.get('correct', 0)}")
    print(f"Accuracy: {metrics.get('accuracy', 0):.2%}")
    
    if metrics.get('by_type'):
        print("\nAccuracy by Type:")
        for test_type, accuracy in metrics['by_type'].items():
            print(f"  {test_type}: {accuracy:.2%}")


def main():
    """Main execution function."""
    
    parser = argparse.ArgumentParser(
        description="Validate evaluation results against quality thresholds"
    )
    parser.add_argument(
        "--results",
        type=str,
        default="results/evaluation_report.json",
        help="Path to evaluation results JSON file"
    )
    parser.add_argument(
        "--min-accuracy",
        type=float,
        help="Minimum required overall accuracy (0.0-1.0)"
    )
    parser.add_argument(
        "--min-correct",
        type=int,
        help="Minimum number of correct answers"
    )
    parser.add_argument(
        "--max-error-rate",
        type=float,
        help="Maximum allowed error rate (0.0-1.0)"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to threshold configuration JSON file"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed results"
    )
    
    args = parser.parse_args()
    
    print("="*70)
    print("CI/CD Threshold Validation")
    print("="*70)
    
    # Load results
    results = load_results(args.results)
    
    # Print summary if verbose
    if args.verbose:
        print_summary(results)
    
    # Build thresholds dictionary
    thresholds = {}
    
    # Load from config file if provided
    if args.config:
        try:
            with open(args.config, 'r') as f:
                thresholds = json.load(f)
            print(f"✓ Loaded thresholds from: {args.config}")
        except Exception as e:
            print(f"✗ Error loading config file: {str(e)}")
            sys.exit(1)
    
    # Override with command-line arguments
    if args.min_accuracy is not None:
        thresholds["min_accuracy"] = args.min_accuracy
    if args.min_correct is not None:
        thresholds["min_correct"] = args.min_correct
    if args.max_error_rate is not None:
        thresholds["max_error_rate"] = args.max_error_rate
    
    # Check if any thresholds are defined
    if not thresholds:
        print("✗ Error: No thresholds defined")
        print("  Use --min-accuracy, --min-correct, --max-error-rate, or --config")
        sys.exit(1)
    
    # Validate thresholds
    all_passed = validate_thresholds(results, thresholds)
    
    # Print final result
    print("\n" + "="*70)
    if all_passed:
        print("✓ ALL CHECKS PASSED")
        print("="*70)
        sys.exit(0)
    else:
        print("✗ SOME CHECKS FAILED")
        print("="*70)
        sys.exit(1)


if __name__ == "__main__":
    main()
