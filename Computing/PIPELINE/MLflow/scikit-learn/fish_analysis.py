"""
Fish Aanalysis with multiple ML models
==================================================

This script provides a complete analysis of the Fish dataset using multiple
machine learning models for both regression (weight prediction) and
classification (species prediction) tasks.

Author: Fish ML
Date: 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Regression models
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR

# Classification models
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB

# Metrics
from sklearn.metrics import (mean_squared_error, r2_score, mean_absolute_error,
                           accuracy_score, classification_report, confusion_matrix)

import warnings
warnings.filterwarnings('ignore')

def load_and_analyze_dataset():
    """Load dataset and perform comprehensive exploratory data analysis."""
    print("=" * 80)
    print("COMPREHENSIVE FISH DATASET ANALYSIS")
    print("=" * 80)
    
    # Load data
    df = pd.read_csv('Dataset/Fish.csv')
    
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Basic info
    print("\n" + "="*50)
    print("DATASET OVERVIEW")
    print("="*50)
    print(f"Number of samples: {len(df)}")
    print(f"Number of features: {len(df.columns) - 1}")  # Excluding target
    print(f"Number of species: {df['Species'].nunique()}")
    
    print("\nSpecies distribution:")
    species_counts = df['Species'].value_counts()
    for species, count in species_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {species:<12}: {count:>3} samples ({percentage:>5.1f}%)")
    
    print(f"\nMissing values: {df.isnull().sum().sum()}")
    
    # Statistical summary
    print("\n" + "="*50)
    print("STATISTICAL SUMMARY")
    print("="*50)
    print(df.describe())
    
    return df

def visualize_data(df):
    """Create comprehensive visualizations of the dataset."""
    print("\n" + "="*50)
    print("DATA VISUALIZATION")
    print("="*50)
    
    # Set up the plotting style
    plt.style.use('default')
    fig = plt.figure(figsize=(20, 15))
    
    # 1. Species distribution
    plt.subplot(3, 4, 1)
    species_counts = df['Species'].value_counts()
    plt.pie(species_counts.values, labels=species_counts.index, autopct='%1.1f%%')
    plt.title('Species Distribution')
    
    # 2. Weight distribution
    plt.subplot(3, 4, 2)
    plt.hist(df['Weight'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
    plt.xlabel('Weight (g)')
    plt.ylabel('Frequency')
    plt.title('Weight Distribution')
    
    # 3. Length measurements comparison
    plt.subplot(3, 4, 3)
    length_cols = ['Length1', 'Length2', 'Length3']
    for col in length_cols:
        plt.hist(df[col], alpha=0.5, label=col, bins=15)
    plt.xlabel('Length (cm)')
    plt.ylabel('Frequency')
    plt.title('Length Measurements Distribution')
    plt.legend()
    
    # 4. Weight vs Length1 by Species
    plt.subplot(3, 4, 4)
    for species in df['Species'].unique():
        species_data = df[df['Species'] == species]
        plt.scatter(species_data['Length1'], species_data['Weight'], 
                   label=species, alpha=0.6, s=30)
    plt.xlabel('Length1 (cm)')
    plt.ylabel('Weight (g)')
    plt.title('Weight vs Length1 by Species')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # 5. Correlation heatmap
    plt.subplot(3, 4, 5)
    numeric_df = df.select_dtypes(include=[np.number])
    correlation_matrix = numeric_df.corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                square=True, fmt='.2f')
    plt.title('Feature Correlation Matrix')
    
    # 6. Box plot of weight by species
    plt.subplot(3, 4, 6)
    df.boxplot(column='Weight', by='Species', ax=plt.gca())
    plt.xticks(rotation=45)
    plt.title('Weight Distribution by Species')
    plt.suptitle('')  # Remove automatic title
    
    # 7. Height vs Width
    plt.subplot(3, 4, 7)
    plt.scatter(df['Height'], df['Width'], alpha=0.6, c=df['Weight'], 
               cmap='viridis', s=30)
    plt.colorbar(label='Weight (g)')
    plt.xlabel('Height (cm)')
    plt.ylabel('Width (cm)')
    plt.title('Height vs Width (colored by Weight)')
    
    # 8. Length ratios
    plt.subplot(3, 4, 8)
    df['L2_L1_ratio'] = df['Length2'] / df['Length1']
    df['L3_L1_ratio'] = df['Length3'] / df['Length1']
    plt.scatter(df['L2_L1_ratio'], df['L3_L1_ratio'], 
               alpha=0.6, c=df['Weight'], cmap='plasma', s=30)
    plt.colorbar(label='Weight (g)')
    plt.xlabel('Length2/Length1 Ratio')
    plt.ylabel('Length3/Length1 Ratio')
    plt.title('Length Ratios (colored by Weight)')
    
    # 9-12. Individual feature distributions by species
    features = ['Length1', 'Height', 'Width', 'Weight']
    for i, feature in enumerate(features, 9):
        plt.subplot(3, 4, i)
        for species in df['Species'].unique():
            species_data = df[df['Species'] == species]
            plt.hist(species_data[feature], alpha=0.5, label=species, bins=10)
        plt.xlabel(f'{feature} {"(g)" if feature == "Weight" else "(cm)"}')
        plt.ylabel('Frequency')
        plt.title(f'{feature} Distribution by Species')
        if i == 9:  # Only show legend for first plot
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.show()
    
    return df

def regression_analysis(df):
    """Perform comprehensive regression analysis for weight prediction."""
    print("\n" + "="*50)
    print("REGRESSION ANALYSIS - WEIGHT PREDICTION")
    print("="*50)
    
    # Prepare data
    X = df.drop(['Weight'], axis=1)
    y = df['Weight']
    
    # Create preprocessor
    categorical_features = ['Species']
    numerical_features = ['Length1', 'Length2', 'Length3', 'Height', 'Width']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(drop='first'), categorical_features),
            ('num', StandardScaler(), numerical_features)
        ]
    )
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42
    )
    
    # Define regression models
    models = {
        'Linear Regression': LinearRegression(),
        'Ridge Regression': Ridge(alpha=1.0),
        'Lasso Regression': Lasso(alpha=0.1),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'Decision Tree': DecisionTreeRegressor(random_state=42),
        'Support Vector': SVR(kernel='rbf', C=100, gamma=0.1)
    }
    
    results = {}
    
    print("\nTraining and evaluating regression models...")
    print("-" * 60)
    
    for name, model in models.items():
        # Create pipeline
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', model)
        ])
        
        # Train model
        pipeline.fit(X_train, y_train)
        
        # Predictions
        y_pred = pipeline.predict(X_test)
        
        # Metrics
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='r2')
        
        results[name] = {
            'MSE': mse, 'RMSE': rmse, 'MAE': mae, 'R2': r2,
            'CV_R2_mean': cv_scores.mean(), 'CV_R2_std': cv_scores.std(),
            'model': pipeline
        }
        
        print(f"{name:<18}: R²={r2:.4f}, RMSE={rmse:.2f}, CV R²={cv_scores.mean():.4f}±{cv_scores.std():.4f}")
    
    # Find best model
    best_model_name = max(results.keys(), key=lambda k: results[k]['R2'])
    best_model = results[best_model_name]['model']
    
    print(f"\nBest regression model: {best_model_name}")
    print(f"Test R² score: {results[best_model_name]['R2']:.4f}")
    
    # Plot results comparison
    plt.figure(figsize=(15, 10))
    
    # R² comparison
    plt.subplot(2, 3, 1)
    model_names = list(results.keys())
    r2_scores = [results[name]['R2'] for name in model_names]
    bars = plt.bar(model_names, r2_scores, color='skyblue', alpha=0.7)
    plt.title('R² Score Comparison')
    plt.ylabel('R² Score')
    plt.xticks(rotation=45)
    plt.ylim(0, 1)
    
    # Add value labels on bars
    for bar, score in zip(bars, r2_scores):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{score:.3f}', ha='center', va='bottom')
    
    # RMSE comparison
    plt.subplot(2, 3, 2)
    rmse_scores = [results[name]['RMSE'] for name in model_names]
    plt.bar(model_names, rmse_scores, color='lightcoral', alpha=0.7)
    plt.title('RMSE Comparison')
    plt.ylabel('RMSE')
    plt.xticks(rotation=45)
    
    # Actual vs Predicted for best model
    plt.subplot(2, 3, 3)
    y_pred_best = best_model.predict(X_test)
    plt.scatter(y_test, y_pred_best, alpha=0.6)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    plt.xlabel('Actual Weight (g)')
    plt.ylabel('Predicted Weight (g)')
    plt.title(f'Actual vs Predicted - {best_model_name}')
    
    # Residuals plot
    plt.subplot(2, 3, 4)
    residuals = y_test - y_pred_best
    plt.scatter(y_pred_best, residuals, alpha=0.6)
    plt.axhline(y=0, color='r', linestyle='--')
    plt.xlabel('Predicted Weight (g)')
    plt.ylabel('Residuals')
    plt.title('Residuals Plot')
    
    # Feature importance (for Random Forest)
    if 'Random Forest' in results:
        plt.subplot(2, 3, 5)
        rf_model = results['Random Forest']['model']
        
        # Get feature names after preprocessing
        feature_names = []
        
        # Get categorical feature names
        cat_features = rf_model.named_steps['preprocessor'].named_transformers_['cat'].get_feature_names_out(['Species'])
        feature_names.extend(cat_features)
        
        # Add numerical feature names
        feature_names.extend(numerical_features)
        
        importances = rf_model.named_steps['regressor'].feature_importances_
        
        # Sort features by importance
        indices = np.argsort(importances)[::-1]
        
        plt.bar(range(len(importances)), importances[indices])
        plt.title('Feature Importance (Random Forest)')
        plt.ylabel('Importance')
        plt.xticks(range(len(importances)), [feature_names[i] for i in indices], rotation=45)
    
    # Cross-validation scores
    plt.subplot(2, 3, 6)
    cv_means = [results[name]['CV_R2_mean'] for name in model_names]
    cv_stds = [results[name]['CV_R2_std'] for name in model_names]
    plt.bar(model_names, cv_means, yerr=cv_stds, capsize=5, color='lightgreen', alpha=0.7)
    plt.title('Cross-validation R² Scores')
    plt.ylabel('CV R² Score')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.show()
    
    return results

def classification_analysis(df):
    """Perform comprehensive classification analysis for species prediction."""
    print("\n" + "="*50)
    print("CLASSIFICATION ANALYSIS - SPECIES PREDICTION")
    print("="*50)
    
    # Prepare data
    X = df.drop(['Species'], axis=1)
    y = df['Species']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Define classification models
    models = {
        'K-Nearest Neighbors': KNeighborsClassifier(n_neighbors=5),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'Support Vector Machine': SVC(kernel='rbf', random_state=42),
        'Naive Bayes': GaussianNB()
    }
    
    results = {}
    
    print("\nTraining and evaluating classification models...")
    print("-" * 60)
    
    for name, model in models.items():
        # Train model
        model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = model.predict(X_test_scaled)
        
        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='accuracy')
        
        results[name] = {
            'Accuracy': accuracy,
            'CV_accuracy_mean': cv_scores.mean(),
            'CV_accuracy_std': cv_scores.std(),
            'model': model,
            'predictions': y_pred
        }
        
        print(f"{name:<22}: Accuracy={accuracy:.4f}, CV Accuracy={cv_scores.mean():.4f}±{cv_scores.std():.4f}")
    
    # Find best model
    best_model_name = max(results.keys(), key=lambda k: results[k]['Accuracy'])
    best_model = results[best_model_name]['model']
    
    print(f"\nBest classification model: {best_model_name}")
    print(f"Test accuracy: {results[best_model_name]['Accuracy']:.4f}")
    
    # Detailed classification report for best model
    print(f"\nDetailed Classification Report - {best_model_name}:")
    print("-" * 60)
    print(classification_report(y_test, results[best_model_name]['predictions']))
    
    # Plot results
    plt.figure(figsize=(15, 10))
    
    # Accuracy comparison
    plt.subplot(2, 3, 1)
    model_names = list(results.keys())
    accuracies = [results[name]['Accuracy'] for name in model_names]
    bars = plt.bar(model_names, accuracies, color='lightblue', alpha=0.7)
    plt.title('Accuracy Comparison')
    plt.ylabel('Accuracy')
    plt.xticks(rotation=45)
    plt.ylim(0, 1)
    
    # Add value labels
    for bar, acc in zip(bars, accuracies):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{acc:.3f}', ha='center', va='bottom')
    
    # Cross-validation scores
    plt.subplot(2, 3, 2)
    cv_means = [results[name]['CV_accuracy_mean'] for name in model_names]
    cv_stds = [results[name]['CV_accuracy_std'] for name in model_names]
    plt.bar(model_names, cv_means, yerr=cv_stds, capsize=5, color='lightcoral', alpha=0.7)
    plt.title('Cross-validation Accuracy')
    plt.ylabel('CV Accuracy')
    plt.xticks(rotation=45)
    
    # Confusion matrix for best model
    plt.subplot(2, 3, 3)
    cm = confusion_matrix(y_test, results[best_model_name]['predictions'])
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=sorted(y_test.unique()),
                yticklabels=sorted(y_test.unique()))
    plt.title(f'Confusion Matrix - {best_model_name}')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    
    # Feature importance (for Random Forest)
    if 'Random Forest' in results:
        plt.subplot(2, 3, 4)
        rf_model = results['Random Forest']['model']
        importances = rf_model.feature_importances_
        feature_names = X.columns
        
        indices = np.argsort(importances)[::-1]
        plt.bar(range(len(importances)), importances[indices])
        plt.title('Feature Importance (Random Forest)')
        plt.ylabel('Importance')
        plt.xticks(range(len(importances)), [feature_names[i] for i in indices], rotation=45)
    
    # Species prediction confidence (for best model if it has predict_proba)
    if hasattr(best_model, 'predict_proba'):
        plt.subplot(2, 3, 5)
        probabilities = best_model.predict_proba(X_test_scaled)
        max_probs = np.max(probabilities, axis=1)
        plt.hist(max_probs, bins=20, alpha=0.7, color='gold')
        plt.xlabel('Prediction Confidence')
        plt.ylabel('Frequency')
        plt.title('Prediction Confidence Distribution')
    
    # Model comparison radar chart
    plt.subplot(2, 3, 6)
    angles = np.linspace(0, 2*np.pi, len(model_names), endpoint=False).tolist()
    angles += angles[:1]  # Complete the circle
    
    accuracies += accuracies[:1]  # Complete the circle
    
    plt.polar(angles, accuracies, 'o-', linewidth=2, color='purple', alpha=0.7)
    plt.fill(angles, accuracies, alpha=0.25, color='purple')
    plt.xticks(angles[:-1], model_names)
    plt.ylim(0, 1)
    plt.title('Model Performance Radar Chart')
    
    plt.tight_layout()
    plt.show()
    
    return results

def generate_insights(df, regression_results, classification_results):
    """Generate key insights from the analysis."""
    print("\n" + "="*50)
    print("KEY INSIGHTS AND RECOMMENDATIONS")
    print("="*50)
    
    # Dataset insights
    print("\n📊 DATASET INSIGHTS:")
    print("-" * 30)
    print(f"• Dataset contains {len(df)} fish samples from {df['Species'].nunique()} species")
    print(f"• Weight ranges from {df['Weight'].min():.1f}g to {df['Weight'].max():.1f}g")
    print(f"• Most common species: {df['Species'].value_counts().index[0]} ({df['Species'].value_counts().iloc[0]} samples)")
    
    # Correlation insights
    numeric_df = df.select_dtypes(include=[np.number])
    weight_corr = numeric_df.corr()['Weight'].abs().sort_values(ascending=False)
    print(f"• Strongest weight predictors: {', '.join(weight_corr.index[1:4])}")
    
    # Regression insights
    print("\n🎯 REGRESSION INSIGHTS (Weight Prediction):")
    print("-" * 40)
    best_reg_model = max(regression_results.keys(), key=lambda k: regression_results[k]['R2'])
    best_r2 = regression_results[best_reg_model]['R2']
    
    print(f"• Best model: {best_reg_model} (R² = {best_r2:.4f})")
    print(f"• Model explains {best_r2*100:.1f}% of weight variance")
    
    if best_r2 > 0.9:
        print("• Excellent predictive performance! ✅")
    elif best_r2 > 0.8:
        print("• Good predictive performance ✅")
    else:
        print("• Moderate predictive performance ⚠️")
    
    # Classification insights
    print("\n🐟 CLASSIFICATION INSIGHTS (Species Prediction):")
    print("-" * 45)
    best_class_model = max(classification_results.keys(), key=lambda k: classification_results[k]['Accuracy'])
    best_acc = classification_results[best_class_model]['Accuracy']
    
    print(f"• Best model: {best_class_model} (Accuracy = {best_acc:.4f})")
    print(f"• Model correctly classifies {best_acc*100:.1f}% of fish species")
    
    if best_acc > 0.95:
        print("• Excellent classification performance! ✅")
    elif best_acc > 0.85:
        print("• Good classification performance ✅")
    else:
        print("• Moderate classification performance ⚠️")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("-" * 20)
    print("• For weight prediction: Use length measurements as primary features")
    print("• For species classification: Physical measurements provide strong discrimination")
    print("• Consider polynomial features for non-linear relationships")
    print("• Collect more data for underrepresented species")
    print("• Validate models on new data before deployment")

def main():
    """Main function to run comprehensive analysis."""
    try:
        # Load and analyze dataset
        df = load_and_analyze_dataset()
        
        # Create visualizations
        df = visualize_data(df)
        
        # Regression analysis
        regression_results = regression_analysis(df)
        
        # Classification analysis
        classification_results = classification_analysis(df)
        
        # Generate insights
        generate_insights(df, regression_results, classification_results)
        
        print("\n" + "="*80)
        print("🎉 COMPREHENSIVE ANALYSIS COMPLETE!")
        print("="*80)
        print("\nAll models have been trained and evaluated.")
        print("Check the plots above for detailed performance comparisons.")
        print("Use the insights to guide your fish prediction applications!")
        
        return df, regression_results, classification_results
        
    except FileNotFoundError:
        print("❌ Error: Dataset/Fish.csv not found!")
        print("Please ensure the Fish.csv file is in the Dataset/ folder.")
        return None, None, None
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return None, None, None

if __name__ == "__main__":
    df, regression_results, classification_results = main()
