"""
Metrics and evaluation utilities for feature learning experiments.
"""

import torch
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from typing import Tuple, Dict, List, Optional
import os


def calculate_reconstruction_loss(reconstructed: np.ndarray, original: np.ndarray, 
                                loss_type: str = 'mse') -> float:
    """
    Calculate reconstruction loss between original and reconstructed data.
    
    Args:
        reconstructed: Reconstructed data
        original: Original data
        loss_type: Type of loss ('mse', 'mae', 'binary_crossentropy')
        
    Returns:
        Reconstruction loss value
    """
    if loss_type == 'mse':
        return np.mean((reconstructed - original) ** 2)
    elif loss_type == 'mae':
        return np.mean(np.abs(reconstructed - original))
    elif loss_type == 'binary_crossentropy':
        # Clip to avoid log(0)
        reconstructed = np.clip(reconstructed, 1e-7, 1 - 1e-7)
        return -np.mean(original * np.log(reconstructed) + (1 - original) * np.log(1 - reconstructed))
    else:
        raise ValueError(f"Unsupported loss type: {loss_type}")


def calculate_accuracy(predictions: np.ndarray, targets: np.ndarray) -> float:
    """
    Calculate classification accuracy.
    
    Args:
        predictions: Model predictions
        targets: True labels
        
    Returns:
        Accuracy score
    """
    return accuracy_score(targets, predictions)


def calculate_precision_recall(predictions: np.ndarray, targets: np.ndarray) -> Tuple[float, float, float]:
    """
    Calculate precision, recall, and F1-score.
    
    Args:
        predictions: Model predictions
        targets: True labels
        
    Returns:
        Tuple of (precision, recall, f1_score)
    """
    precision, recall, f1, _ = precision_recall_fscore_support(targets, predictions, average='weighted')
    return precision, recall, f1


def plot_training_curves(train_losses: List[float], val_losses: List[float], 
                        train_accuracies: List[float], val_accuracies: List[float],
                        save_path: str = None) -> None:
    """
    Plot training curves for loss and accuracy.
    
    Args:
        train_losses: Training losses per epoch
        val_losses: Validation losses per epoch
        train_accuracies: Training accuracies per epoch
        val_accuracies: Validation accuracies per epoch
        save_path: Path to save the plot
    """
    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Plot losses
        epochs = range(1, len(train_losses) + 1)
        ax1.plot(epochs, train_losses, 'b-', label='Training Loss')
        ax1.plot(epochs, val_losses, 'r-', label='Validation Loss')
        ax1.set_title('Training and Validation Loss')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.legend()
        ax1.grid(True)
        
        # Plot accuracies
        ax2.plot(epochs, train_accuracies, 'b-', label='Training Accuracy')
        ax2.plot(epochs, val_accuracies, 'r-', label='Validation Accuracy')
        ax2.set_title('Training and Validation Accuracy')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Accuracy (%)')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Training curves saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
        
    except Exception as e:
        print(f"Error plotting training curves: {e}")


def evaluate_features(features: np.ndarray, labels: np.ndarray, 
                     test_features: np.ndarray = None, test_labels: np.ndarray = None) -> Dict:
    """
    Evaluate the quality of extracted features using various downstream tasks.
    
    Args:
        features: Training features
        labels: Training labels
        test_features: Test features (optional)
        test_labels: Test labels (optional)
        
    Returns:
        Dictionary with evaluation results
    """
    results = {}
    
    # If test data not provided, use train data for evaluation
    if test_features is None:
        test_features = features
        test_labels = labels
    
    # 1. K-Nearest Neighbors classification
    try:
        knn = KNeighborsClassifier(n_neighbors=5)
        knn.fit(features, labels)
        knn_pred = knn.predict(test_features)
        results['knn_accuracy'] = calculate_accuracy(knn_pred, test_labels)
        
        precision, recall, f1 = calculate_precision_recall(knn_pred, test_labels)
        results['knn_precision'] = precision
        results['knn_recall'] = recall
        results['knn_f1'] = f1
    except Exception as e:
        print(f"Error in KNN evaluation: {e}")
        results['knn_accuracy'] = 0.0
    
    # 2. SVM classification
    try:
        svm = SVC(kernel='rbf', random_state=42)
        svm.fit(features, labels)
        svm_pred = svm.predict(test_features)
        results['svm_accuracy'] = calculate_accuracy(svm_pred, test_labels)
        
        precision, recall, f1 = calculate_precision_recall(svm_pred, test_labels)
        results['svm_precision'] = precision
        results['svm_recall'] = recall
        results['svm_f1'] = f1
    except Exception as e:
        print(f"Error in SVM evaluation: {e}")
        results['svm_accuracy'] = 0.0
    
    # 3. Logistic Regression classification
    try:
        lr = LogisticRegression(random_state=42, max_iter=1000)
        lr.fit(features, labels)
        lr_pred = lr.predict(test_features)
        results['lr_accuracy'] = calculate_accuracy(lr_pred, test_labels)
        
        precision, recall, f1 = calculate_precision_recall(lr_pred, test_labels)
        results['lr_precision'] = precision
        results['lr_recall'] = recall
        results['lr_f1'] = f1
    except Exception as e:
        print(f"Error in Logistic Regression evaluation: {e}")
        results['lr_accuracy'] = 0.0
    
    # 4. Clustering evaluation (unsupervised)
    try:
        if len(np.unique(labels)) > 1:  # Ensure we have multiple classes
            kmeans = KMeans(n_clusters=len(np.unique(labels)), random_state=42)
            cluster_pred = kmeans.fit_predict(features)
            
            # Calculate silhouette score (approximate using inertia)
            results['kmeans_inertia'] = kmeans.inertia_
            
            # Calculate cluster purity (how well clusters match true labels)
            results['cluster_purity'] = calculate_cluster_purity(cluster_pred, labels)
    except Exception as e:
        print(f"Error in clustering evaluation: {e}")
        results['kmeans_inertia'] = 0.0
        results['cluster_purity'] = 0.0
    
    return results


def calculate_cluster_purity(cluster_pred: np.ndarray, true_labels: np.ndarray) -> float:
    """
    Calculate clustering purity score.
    
    Args:
        cluster_pred: Predicted cluster assignments
        true_labels: True class labels
        
    Returns:
        Purity score
    """
    total_correct = 0
    total_samples = len(cluster_pred)
    
    for cluster_id in np.unique(cluster_pred):
        cluster_mask = cluster_pred == cluster_id
        cluster_true_labels = true_labels[cluster_mask]
        
        if len(cluster_true_labels) > 0:
            # Most common true label in this cluster
            most_common_label = np.bincount(cluster_true_labels).argmax()
            correct_in_cluster = np.sum(cluster_true_labels == most_common_label)
            total_correct += correct_in_cluster
    
    return total_correct / total_samples


def plot_confusion_matrix(predictions: np.ndarray, targets: np.ndarray, 
                         class_names: List[str] = None, save_path: str = None) -> None:
    """
    Plot confusion matrix.
    
    Args:
        predictions: Model predictions
        targets: True labels
        class_names: Names of classes
        save_path: Path to save the plot
    """
    try:
        cm = confusion_matrix(targets, predictions)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=class_names, yticklabels=class_names)
        plt.title('Confusion Matrix')
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
        
        plt.close()
        
    except Exception as e:
        print(f"Error plotting confusion matrix: {e}")


def calculate_feature_statistics(features: np.ndarray) -> Dict:
    """
    Calculate statistics for feature representations.
    
    Args:
        features: Feature matrix [num_samples, num_features]
        
    Returns:
        Dictionary with feature statistics
    """
    stats = {
        'num_samples': features.shape[0],
        'num_features': features.shape[1],
        'mean': np.mean(features, axis=0).mean(),
        'std': np.std(features, axis=0).mean(),
        'min': np.min(features),
        'max': np.max(features),
        'sparsity': np.mean(features == 0),  # Proportion of zero values
    }
    
    # Calculate pairwise cosine similarities (sample a subset for efficiency)
    try:
        if features.shape[0] > 1000:
            idx = np.random.choice(features.shape[0], 1000, replace=False)
            sample_features = features[idx]
        else:
            sample_features = features
        
        # Normalize features
        norms = np.linalg.norm(sample_features, axis=1, keepdims=True)
        normalized_features = sample_features / (norms + 1e-8)
        
        # Calculate cosine similarity matrix
        similarity_matrix = np.dot(normalized_features, normalized_features.T)
        
        # Extract upper triangular part (excluding diagonal)
        upper_tri_idx = np.triu_indices_from(similarity_matrix, k=1)
        similarities = similarity_matrix[upper_tri_idx]
        
        stats['avg_cosine_similarity'] = np.mean(similarities)
        stats['std_cosine_similarity'] = np.std(similarities)
        
    except Exception as e:
        print(f"Error calculating cosine similarities: {e}")
        stats['avg_cosine_similarity'] = 0.0
        stats['std_cosine_similarity'] = 0.0
    
    return stats


def compare_feature_methods(features_dict: Dict[str, Tuple[np.ndarray, np.ndarray]], 
                           save_path: str = None) -> Dict:
    """
    Compare different feature extraction methods.
    
    Args:
        features_dict: Dictionary with method_name -> (features, labels) pairs
        save_path: Path to save comparison results
        
    Returns:
        Dictionary with comparison results
    """
    comparison_results = {}
    
    for method_name, (features, labels) in features_dict.items():
        print(f"Evaluating {method_name}...")
        
        # Calculate feature statistics
        stats = calculate_feature_statistics(features)
        
        # Evaluate downstream task performance
        eval_results = evaluate_features(features, labels)
        
        # Combine results
        method_results = {**stats, **eval_results}
        comparison_results[method_name] = method_results
    
    # Create comparison plot
    if save_path and len(features_dict) > 1:
        try:
            create_comparison_plot(comparison_results, save_path)
        except Exception as e:
            print(f"Error creating comparison plot: {e}")
    
    return comparison_results


def create_comparison_plot(results: Dict, save_path: str) -> None:
    """Create a comparison plot of different feature methods."""
    try:
        methods = list(results.keys())
        metrics = ['knn_accuracy', 'svm_accuracy', 'lr_accuracy', 'cluster_purity']
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(methods))
        width = 0.2
        
        for i, metric in enumerate(metrics):
            values = [results[method].get(metric, 0) for method in methods]
            ax.bar(x + i * width, values, width, label=metric.replace('_', ' ').title())
        
        ax.set_xlabel('Feature Extraction Method')
        ax.set_ylabel('Score')
        ax.set_title('Feature Extraction Method Comparison')
        ax.set_xticks(x + width * 1.5)
        ax.set_xticklabels(methods)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Comparison plot saved to {save_path}")
        
    except Exception as e:
        print(f"Error creating comparison plot: {e}")


if __name__ == "__main__":
    # Test metrics functions
    print("Testing metrics functions...")
    
    # Generate sample data
    np.random.seed(42)
    features = np.random.randn(100, 50)
    labels = np.random.randint(0, 5, 100)
    predictions = np.random.randint(0, 5, 100)
    
    # Test accuracy calculation
    accuracy = calculate_accuracy(predictions, labels)
    print(f"Sample accuracy: {accuracy:.3f}")
    
    # Test feature evaluation
    eval_results = evaluate_features(features, labels)
    print("Feature evaluation results:")
    for key, value in eval_results.items():
        print(f"  {key}: {value:.3f}")
    
    # Test feature statistics
    stats = calculate_feature_statistics(features)
    print("Feature statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value:.3f}")
    
    print("Metrics test completed!")
