#!/usr/bin/env python3
"""
Feature evaluation script for the Feature Learning project.
"""

import os
import sys
import numpy as np
import argparse
from typing import Dict, Tuple, List
import json

def load_features(features_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load features from a .npz file.
    
    Args:
        features_path: Path to the .npz file containing features and labels
        
    Returns:
        Tuple of (features, labels)
    """
    try:
        data = np.load(features_path)
        features = data['features']
        labels = data['labels']
        return features, labels
    except Exception as e:
        print(f"Error loading features from {features_path}: {e}")
        return None, None


def calculate_basic_metrics(features: np.ndarray, labels: np.ndarray) -> Dict:
    """
    Calculate basic metrics for feature evaluation.
    
    Args:
        features: Feature array [num_samples, num_features]
        labels: Label array [num_samples]
        
    Returns:
        Dictionary with basic metrics
    """
    metrics = {}
    
    # Basic statistics
    metrics['num_samples'] = features.shape[0]
    metrics['num_features'] = features.shape[1]
    metrics['num_classes'] = len(np.unique(labels))
    
    # Feature statistics
    metrics['feature_mean'] = float(np.mean(features))
    metrics['feature_std'] = float(np.std(features))
    metrics['feature_min'] = float(np.min(features))
    metrics['feature_max'] = float(np.max(features))
    
    # Sparsity (proportion of near-zero values)
    threshold = 1e-6
    metrics['sparsity'] = float(np.mean(np.abs(features) < threshold))
    
    return metrics


def evaluate_feature_separability(features: np.ndarray, labels: np.ndarray) -> Dict:
    """
    Evaluate how well features separate different classes.
    
    Args:
        features: Feature array
        labels: Label array
        
    Returns:
        Dictionary with separability metrics
    """
    metrics = {}
    
    try:
        unique_labels = np.unique(labels)
        
        # Calculate within-class and between-class distances
        within_class_distances = []
        between_class_distances = []
        
        for label in unique_labels:
            class_features = features[labels == label]
            
            if len(class_features) > 1:
                # Within-class distances (sample a subset for efficiency)
                n_samples = min(100, len(class_features))
                idx = np.random.choice(len(class_features), n_samples, replace=False)
                sample_features = class_features[idx]
                
                for i in range(len(sample_features)):
                    for j in range(i+1, len(sample_features)):
                        dist = np.linalg.norm(sample_features[i] - sample_features[j])
                        within_class_distances.append(dist)
            
            # Between-class distances
            other_labels = unique_labels[unique_labels != label]
            for other_label in other_labels:
                other_class_features = features[labels == other_label]
                
                if len(class_features) > 0 and len(other_class_features) > 0:
                    # Sample a few points from each class
                    n_samples = min(20, len(class_features), len(other_class_features))
                    
                    class_idx = np.random.choice(len(class_features), n_samples, replace=False)
                    other_idx = np.random.choice(len(other_class_features), n_samples, replace=False)
                    
                    class_sample = class_features[class_idx]
                    other_sample = other_class_features[other_idx]
                    
                    for i in range(len(class_sample)):
                        for j in range(len(other_sample)):
                            dist = np.linalg.norm(class_sample[i] - other_sample[j])
                            between_class_distances.append(dist)
        
        if within_class_distances and between_class_distances:
            metrics['avg_within_class_distance'] = float(np.mean(within_class_distances))
            metrics['avg_between_class_distance'] = float(np.mean(between_class_distances))
            
            # Separability ratio (higher is better)
            metrics['separability_ratio'] = float(
                np.mean(between_class_distances) / (np.mean(within_class_distances) + 1e-8)
            )
        else:
            metrics['avg_within_class_distance'] = 0.0
            metrics['avg_between_class_distance'] = 0.0
            metrics['separability_ratio'] = 0.0
    
    except Exception as e:
        print(f"Error calculating separability metrics: {e}")
        metrics['avg_within_class_distance'] = 0.0
        metrics['avg_between_class_distance'] = 0.0
        metrics['separability_ratio'] = 0.0
    
    return metrics


def evaluate_model_features(features_path: str, output_path: str = None) -> Dict:
    """
    Evaluate features extracted from a model.
    
    Args:
        features_path: Path to the features file (.npz)
        output_path: Path to save evaluation results (JSON)
        
    Returns:
        Dictionary with evaluation results
    """
    print(f"Evaluating features from {features_path}")
    
    # Load features
    features, labels = load_features(features_path)
    if features is None or labels is None:
        return {}
    
    print(f"Loaded {features.shape[0]} samples with {features.shape[1]} features")
    
    # Calculate metrics
    results = {}
    
    # Basic metrics
    basic_metrics = calculate_basic_metrics(features, labels)
    results['basic_metrics'] = basic_metrics
    
    # Separability metrics
    separability_metrics = evaluate_feature_separability(features, labels)
    results['separability_metrics'] = separability_metrics
    
    # Print summary
    print("\nFEATURE EVALUATION RESULTS")
    print("=" * 40)
    print(f"Samples: {basic_metrics['num_samples']}")
    print(f"Features: {basic_metrics['num_features']}")
    print(f"Classes: {basic_metrics['num_classes']}")
    print(f"Feature Range: [{basic_metrics['feature_min']:.3f}, {basic_metrics['feature_max']:.3f}]")
    print(f"Feature Mean: {basic_metrics['feature_mean']:.3f}")
    print(f"Feature Std: {basic_metrics['feature_std']:.3f}")
    print(f"Sparsity: {basic_metrics['sparsity']:.3f}")
    print(f"Separability Ratio: {separability_metrics.get('separability_ratio', 0):.3f}")
    print("=" * 40)
    
    # Save results
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {output_path}")
    
    return results


def compare_feature_methods(feature_paths: Dict[str, str], output_dir: str = "results") -> Dict:
    """
    Compare multiple feature extraction methods.
    
    Args:
        feature_paths: Dictionary mapping method names to feature file paths
        output_dir: Directory to save comparison results
        
    Returns:
        Dictionary with comparison results
    """
    print("Comparing feature extraction methods...")
    
    comparison_results = {}
    
    for method_name, features_path in feature_paths.items():
        print(f"\nEvaluating {method_name}...")
        
        if os.path.exists(features_path):
            results = evaluate_model_features(features_path)
            comparison_results[method_name] = results
        else:
            print(f"⚠️ Features file not found: {features_path}")
            comparison_results[method_name] = {}
    
    # Save comparison results
    os.makedirs(output_dir, exist_ok=True)
    comparison_path = os.path.join(output_dir, "feature_comparison.json")
    
    with open(comparison_path, 'w') as f:
        json.dump(comparison_results, f, indent=2)
    
    print(f"\nComparison results saved to {comparison_path}")
    
    # Print comparison summary
    print("\nFEATURE METHOD COMPARISON")
    print("=" * 50)
    
    for method_name, results in comparison_results.items():
        if results and 'basic_metrics' in results:
            basic = results['basic_metrics']
            sep = results.get('separability_metrics', {})
            
            print(f"\n{method_name}:")
            print(f"  Features: {basic.get('num_features', 'N/A')}")
            print(f"  Feature Std: {basic.get('feature_std', 0):.3f}")
            print(f"  Separability: {sep.get('separability_ratio', 0):.3f}")
        else:
            print(f"\n{method_name}: No results available")
    
    print("=" * 50)
    
    return comparison_results


def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(description='Evaluate extracted features')
    parser.add_argument('--features-path', type=str, default='results/cnn_features.npz',
                       help='Path to features file (.npz)')
    parser.add_argument('--output-path', type=str, default='results/feature_evaluation.json',
                       help='Path to save evaluation results')
    parser.add_argument('--compare', action='store_true',
                       help='Compare multiple feature methods')
    
    args = parser.parse_args()
    
    if args.compare:
        # Look for multiple feature files
        feature_paths = {}
        
        # Common feature file patterns
        patterns = {
            'CNN': 'results/cnn_features.npz',
            'RNN': 'results/rnn_features.npz', 
            'Autoencoder': 'results/autoencoder_features.npz',
            'Transfer': 'results/transfer_features.npz'
        }
        
        # Find existing feature files
        for method, path in patterns.items():
            if os.path.exists(path):
                feature_paths[method] = path
        
        if feature_paths:
            compare_feature_methods(feature_paths)
        else:
            print("❌ No feature files found for comparison")
    
    else:
        # Evaluate single feature file
        if os.path.exists(args.features_path):
            evaluate_model_features(args.features_path, args.output_path)
        else:
            print(f"❌ Features file not found: {args.features_path}")


if __name__ == "__main__":
    main()
