"""
Fish weight prediction using Linear Regression
==============================================

This script demonstrates how to predict fish weight using linear regression
with the Fish.csv dataset. It includes data preprocessing, model training,
evaluation, and example predictions.

Author: Fish ML Project
Date: 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
import warnings
warnings.filterwarnings('ignore')

def load_and_explore_data():
    """Load the Fish dataset and perform basic exploration."""
    print("=" * 60)
    print("FISH WEIGHT PREDICTION USING LINEAR REGRESSION")
    print("=" * 60)
    
    # Load the data
    df = pd.read_csv('Dataset/Fish.csv')
    
    print(f"\nDataset Shape: {df.shape}")
    print(f"Features: {list(df.columns)}")
    print("\nFirst 5 rows:")
    print(df.head())
    
    print("\nDataset Info:")
    print(df.info())
    
    print("\nBasic Statistics:")
    print(df.describe())
    
    print("\nSpecies distribution:")
    print(df['Species'].value_counts())
    
    print("\nMissing values:")
    print(df.isnull().sum())
    
    return df

def preprocess_data(df):
    """Preprocess the data for machine learning."""
    print("\n" + "=" * 40)
    print("DATA PREPROCESSING")
    print("=" * 40)
    
    # Separate features and target
    X = df.drop('Weight', axis=1)
    y = df['Weight']
    
    print(f"Features shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    
    # Identify categorical and numerical features
    categorical_features = ['Species']
    numerical_features = ['Length1', 'Length2', 'Length3', 'Height', 'Width']
    
    print(f"Categorical features: {categorical_features}")
    print(f"Numerical features: {numerical_features}")
    
    # Create preprocessor for one-hot encoding
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', drop='first'), categorical_features)
        ],
        remainder='passthrough'  # Keep numerical features as they are
    )
    
    # Apply preprocessing
    X_processed = preprocessor.fit_transform(X)
    
    # Get feature names after preprocessing
    cat_feature_names = preprocessor.named_transformers_['cat'].get_feature_names_out(categorical_features)
    all_feature_names = list(cat_feature_names) + numerical_features
    
    print(f"Features after preprocessing: {len(all_feature_names)}")
    print(f"Feature names: {all_feature_names}")
    
    return X_processed, y, preprocessor, all_feature_names

def train_and_evaluate_model(X, y):
    """Train linear regression model and evaluate its performance."""
    print("\n" + "=" * 40)
    print("MODEL TRAINING AND EVALUATION")
    print("=" * 40)
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=None
    )
    
    print(f"Training set size: {X_train.shape[0]}")
    print(f"Test set size: {X_test.shape[0]}")
    
    # Initialize and train the model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Make predictions
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    # Calculate metrics
    train_mse = mean_squared_error(y_train, y_train_pred)
    test_mse = mean_squared_error(y_test, y_test_pred)
    train_r2 = r2_score(y_train, y_train_pred)
    test_r2 = r2_score(y_test, y_test_pred)
    train_mae = mean_absolute_error(y_train, y_train_pred)
    test_mae = mean_absolute_error(y_test, y_test_pred)
    
    print("\nModel Performance:")
    print("-" * 40)
    print(f"Training Set:")
    print(f"  MSE: {train_mse:.2f}")
    print(f"  RMSE: {np.sqrt(train_mse):.2f}")
    print(f"  MAE: {train_mae:.2f}")
    print(f"  R²: {train_r2:.4f}")
    
    print(f"\nTest Set:")
    print(f"  MSE: {test_mse:.2f}")
    print(f"  RMSE: {np.sqrt(test_mse):.2f}")
    print(f"  MAE: {test_mae:.2f}")
    print(f"  R²: {test_r2:.4f}")
    
    # Check for overfitting
    if train_r2 - test_r2 > 0.1:
        print(f"\n⚠️  Potential overfitting detected!")
        print(f"   Training R² - Test R² = {train_r2 - test_r2:.4f}")
    else:
        print(f"\n✅ Good model generalization!")
    
    return model, X_train, X_test, y_train, y_test, y_test_pred

def plot_predictions(y_test, y_pred):
    """Plot actual vs predicted values."""
    plt.figure(figsize=(10, 6))
    
    plt.subplot(1, 2, 1)
    plt.scatter(y_test, y_pred, alpha=0.7)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    plt.xlabel('Actual Weight (g)')
    plt.ylabel('Predicted Weight (g)')
    plt.title('Actual vs Predicted Weight')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    residuals = y_test - y_pred
    plt.scatter(y_pred, residuals, alpha=0.7)
    plt.axhline(y=0, color='r', linestyle='--')
    plt.xlabel('Predicted Weight (g)')
    plt.ylabel('Residuals (g)')
    plt.title('Residual Plot')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def feature_importance_analysis(model, feature_names):
    """Analyze feature importance."""
    print("\n" + "=" * 40)
    print("FEATURE IMPORTANCE ANALYSIS")
    print("=" * 40)
    
    # Get coefficients
    coefficients = model.coef_
    
    # Create feature importance dataframe
    feature_importance = pd.DataFrame({
        'Feature': feature_names,
        'Coefficient': coefficients,
        'Abs_Coefficient': np.abs(coefficients)
    })
    
    # Sort by absolute coefficient value
    feature_importance = feature_importance.sort_values('Abs_Coefficient', ascending=False)
    
    print("\nFeature Importance (by absolute coefficient value):")
    print("-" * 50)
    for idx, row in feature_importance.head(10).iterrows():
        print(f"{row['Feature']:<20}: {row['Coefficient']:>8.4f}")
    
    return feature_importance

def make_sample_predictions(model, preprocessor, df):
    """Make predictions on sample data."""
    print("\n" + "=" * 40)
    print("SAMPLE PREDICTIONS")
    print("=" * 40)
    
    # Sample data points from different species
    species_samples = {}
    for species in df['Species'].unique():
        species_data = df[df['Species'] == species].iloc[0]
        species_samples[species] = species_data
    
    print("\nPredictions for sample fish from each species:")
    print("-" * 60)
    
    for species, sample in species_samples.items():
        # Prepare sample for prediction
        sample_features = sample.drop('Weight').values.reshape(1, -1)
        sample_df = pd.DataFrame([sample.drop('Weight')], columns=df.columns[:-1])
        
        # Preprocess the sample
        sample_processed = preprocessor.transform(sample_df)
        
        # Make prediction
        predicted_weight = model.predict(sample_processed)[0]
        actual_weight = sample['Weight']
        
        print(f"{species:<15}: Actual={actual_weight:>6.1f}g, Predicted={predicted_weight:>6.1f}g, "
              f"Error={abs(actual_weight - predicted_weight):>5.1f}g")

def create_prediction_function(model, preprocessor, feature_names):
    """Create a convenient prediction function."""
    def predict_fish_weight(species, length1, length2, length3, height, width):
        """
        Predict fish weight based on species and measurements.
        
        Parameters:
        - species: str, fish species name
        - length1: float, vertical length in cm
        - length2: float, diagonal length in cm
        - length3: float, cross length in cm
        - height: float, height in cm
        - width: float, width in cm
        
        Returns:
        - predicted_weight: float, predicted weight in grams
        """
        # Create input dataframe
        input_data = pd.DataFrame({
            'Species': [species],
            'Length1': [length1],
            'Length2': [length2],
            'Length3': [length3],
            'Height': [height],
            'Width': [width]
        })
        
        # Preprocess
        input_processed = preprocessor.transform(input_data)
        
        # Predict
        prediction = model.predict(input_processed)[0]
        return prediction
    
    return predict_fish_weight

def main():
    """Main function to run the complete analysis."""
    try:
        # Load and explore data
        df = load_and_explore_data()
        
        # Preprocess data
        X_processed, y, preprocessor, feature_names = preprocess_data(df)
        
        # Train and evaluate model
        model, X_train, X_test, y_train, y_test, y_pred = train_and_evaluate_model(X_processed, y)
        
        # Plot predictions
        plot_predictions(y_test, y_pred)
        
        # Feature importance analysis
        feature_importance = feature_importance_analysis(model, feature_names)
        
        # Sample predictions
        make_sample_predictions(model, preprocessor, df)
        
        # Create prediction function
        predict_weight = create_prediction_function(model, preprocessor, feature_names)
        
        # Example usage of prediction function
        print("\n" + "=" * 40)
        print("EXAMPLE PREDICTIONS")
        print("=" * 40)
        
        # Example predictions
        examples = [
            ('Bream', 23.2, 25.4, 30.0, 11.52, 4.02),
            ('Pike', 37.0, 40.0, 42.5, 12.5, 5.1),
            ('Roach', 19.0, 20.5, 22.8, 8.5, 3.2)
        ]
        
        print("\nExample predictions:")
        print("-" * 50)
        for species, l1, l2, l3, h, w in examples:
            pred_weight = predict_weight(species, l1, l2, l3, h, w)
            print(f"{species}: {pred_weight:.1f}g (L1={l1}, L2={l2}, L3={l3}, H={h}, W={w})")
        
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE! 🎣")
        print("=" * 60)
        
        return model, preprocessor, predict_weight
        
    except FileNotFoundError:
        print("Error: Dataset/Fish.csv not found!")
        print("Please make sure the Fish.csv file is in the Dataset/ folder.")
        return None, None, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None, None

if __name__ == "__main__":
    model, preprocessor, predict_weight = main()
