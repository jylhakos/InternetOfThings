#!/usr/bin/env python3
"""
Data Preprocessing Pipeline for Fish Weight Prediction
This script handles data loading, cleaning, and preprocessing for the MLflow pipeline.
"""

import pandas as pd
import numpy as np
import os
import logging
import mlflow
import mlflow.sklearn
from sklearn.preprocessing import StandardScaler, LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPreprocessor:
    def __init__(self, data_path='Dataset/Fish.csv'):
        self.data_path = data_path
        self.df = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
    def load_data(self):
        """Load the fish dataset from CSV file"""
        try:
            if os.path.exists(self.data_path):
                self.df = pd.read_csv(self.data_path)
                logger.info(f"Dataset loaded successfully from {self.data_path}")
                logger.info(f"Dataset shape: {self.df.shape}")
                return True
            else:
                logger.error(f"Dataset not found at {self.data_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            return False
    
    def explore_data(self):
        """Perform exploratory data analysis"""
        if self.df is None:
            logger.error("No data loaded. Please load data first.")
            return
        
        logger.info("=== EXPLORATORY DATA ANALYSIS ===")
        
        # Basic information
        logger.info(f"Dataset shape: {self.df.shape}")
        logger.info(f"Column names: {list(self.df.columns)}")
        logger.info(f"Data types:\n{self.df.dtypes}")
        
        # Missing values
        missing_values = self.df.isnull().sum()
        logger.info(f"Missing values:\n{missing_values}")
        
        # Statistical summary
        logger.info(f"Statistical summary:\n{self.df.describe()}")
        
        # Species distribution
        species_counts = self.df['Species'].value_counts()
        logger.info(f"Species distribution:\n{species_counts}")
        
        return {
            'shape': self.df.shape,
            'columns': list(self.df.columns),
            'missing_values': missing_values.to_dict(),
            'species_counts': species_counts.to_dict()
        }
    
    def clean_data(self):
        """Clean the dataset"""
        if self.df is None:
            logger.error("No data loaded. Please load data first.")
            return
        
        logger.info("=== DATA CLEANING ===")
        
        # Check for missing values
        initial_shape = self.df.shape
        logger.info(f"Initial dataset shape: {initial_shape}")
        
        # Remove rows with missing values
        self.df = self.df.dropna()
        logger.info(f"After removing missing values: {self.df.shape}")
        
        # Remove outliers using IQR method for Weight
        Q1 = self.df['Weight'].quantile(0.25)
        Q3 = self.df['Weight'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers_mask = (self.df['Weight'] >= lower_bound) & (self.df['Weight'] <= upper_bound)
        self.df = self.df[outliers_mask]
        logger.info(f"After removing outliers: {self.df.shape}")
        
        # Ensure all numeric columns are properly typed
        numeric_columns = ['Weight', 'Length1', 'Length2', 'Length3', 'Height', 'Width']
        for col in numeric_columns:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Remove any rows that became NaN after conversion
        self.df = self.df.dropna()
        logger.info(f"Final cleaned dataset shape: {self.df.shape}")
        
        return self.df
    
    def feature_engineering(self):
        """Create additional features from existing ones"""
        if self.df is None:
            logger.error("No data loaded. Please load data first.")
            return
        
        logger.info("=== FEATURE ENGINEERING ===")
        
        # Create new features
        self.df['Length_avg'] = (self.df['Length1'] + self.df['Length2'] + self.df['Length3']) / 3
        self.df['Volume_proxy'] = self.df['Length_avg'] * self.df['Height'] * self.df['Width']
        self.df['Length_diff'] = self.df['Length3'] - self.df['Length1']
        self.df['Aspect_ratio'] = self.df['Length_avg'] / self.df['Height']
        self.df['Body_index'] = self.df['Height'] / self.df['Width']
        
        # Encode species as numeric
        self.df['Species_encoded'] = self.label_encoder.fit_transform(self.df['Species'])
        
        logger.info(f"New features created: {['Length_avg', 'Volume_proxy', 'Length_diff', 'Aspect_ratio', 'Body_index', 'Species_encoded']}")
        
        return self.df
    
    def create_visualizations(self):
        """Create comprehensive data visualizations"""
        if self.df is None:
            logger.error("No data loaded. Please load data first.")
            return
        
        logger.info("=== CREATING VISUALIZATIONS ===")
        
        # Create output directory for plots
        os.makedirs('plots', exist_ok=True)
        
        # 1. Species distribution
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        self.df['Species'].value_counts().plot(kind='bar')
        plt.title('Fish Species Distribution')
        plt.xlabel('Species')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        
        # 2. Weight distribution
        plt.subplot(1, 2, 2)
        plt.hist(self.df['Weight'], bins=30, alpha=0.7)
        plt.title('Weight Distribution')
        plt.xlabel('Weight (g)')
        plt.ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig('plots/species_weight_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Correlation matrix
        plt.figure(figsize=(12, 10))
        numeric_cols = ['Weight', 'Length1', 'Length2', 'Length3', 'Height', 'Width', 
                       'Length_avg', 'Volume_proxy', 'Length_diff', 'Aspect_ratio', 'Body_index']
        correlation_matrix = self.df[numeric_cols].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title('Feature Correlation Matrix')
        plt.tight_layout()
        plt.savefig('plots/correlation_matrix.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. Weight vs Length relationships
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        axes[0,0].scatter(self.df['Length1'], self.df['Weight'], alpha=0.6)
        axes[0,0].set_xlabel('Length1')
        axes[0,0].set_ylabel('Weight')
        axes[0,0].set_title('Weight vs Length1')
        
        axes[0,1].scatter(self.df['Length2'], self.df['Weight'], alpha=0.6)
        axes[0,1].set_xlabel('Length2')
        axes[0,1].set_ylabel('Weight')
        axes[0,1].set_title('Weight vs Length2')
        
        axes[1,0].scatter(self.df['Length3'], self.df['Weight'], alpha=0.6)
        axes[1,0].set_xlabel('Length3')
        axes[1,0].set_ylabel('Weight')
        axes[1,0].set_title('Weight vs Length3')
        
        axes[1,1].scatter(self.df['Volume_proxy'], self.df['Weight'], alpha=0.6)
        axes[1,1].set_xlabel('Volume Proxy')
        axes[1,1].set_ylabel('Weight')
        axes[1,1].set_title('Weight vs Volume Proxy')
        
        plt.tight_layout()
        plt.savefig('plots/weight_vs_features.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 5. Interactive plotly visualization
        fig = px.scatter_matrix(
            self.df[['Weight', 'Length1', 'Length2', 'Length3', 'Height', 'Width']], 
            color=self.df['Species'],
            title="Fish Measurements Scatter Matrix"
        )
        fig.write_html('plots/interactive_scatter_matrix.html')
        
        logger.info("Visualizations saved to 'plots' directory")
    
    def prepare_features_target(self):
        """Prepare feature matrix and target variable"""
        if self.df is None:
            logger.error("No data loaded. Please load data first.")
            return None, None
        
        # Define feature columns
        feature_columns = ['Length1', 'Length2', 'Length3', 'Height', 'Width', 
                          'Length_avg', 'Volume_proxy', 'Length_diff', 'Aspect_ratio', 
                          'Body_index', 'Species_encoded']
        
        X = self.df[feature_columns]
        y = self.df['Weight']
        
        logger.info(f"Features shape: {X.shape}")
        logger.info(f"Target shape: {y.shape}")
        logger.info(f"Feature columns: {feature_columns}")
        
        return X, y
    
    def save_processed_data(self, output_path='processed_data'):
        """Save processed data for use in training"""
        if self.df is None:
            logger.error("No data loaded. Please load data first.")
            return
        
        os.makedirs(output_path, exist_ok=True)
        
        # Save processed dataset
        self.df.to_csv(f'{output_path}/processed_fish_data.csv', index=False)
        
        # Save feature matrix and target
        X, y = self.prepare_features_target()
        if X is not None and y is not None:
            X.to_csv(f'{output_path}/features.csv', index=False)
            y.to_csv(f'{output_path}/target.csv', index=False)
        
        logger.info(f"Processed data saved to {output_path}")

def main():
    """Main preprocessing pipeline"""
    with mlflow.start_run(run_name="data_preprocessing"):
        
        # Initialize preprocessor
        preprocessor = DataPreprocessor()
        
        # Load data
        if not preprocessor.load_data():
            return
        
        # Explore data
        eda_results = preprocessor.explore_data()
        
        # Log EDA results to MLflow
        mlflow.log_param("initial_dataset_shape", eda_results['shape'])
        mlflow.log_param("number_of_features", len(eda_results['columns']))
        mlflow.log_param("species_count", len(eda_results['species_counts']))
        
        for species, count in eda_results['species_counts'].items():
            mlflow.log_metric(f"species_{species}_count", count)
        
        # Clean data
        cleaned_data = preprocessor.clean_data()
        mlflow.log_param("cleaned_dataset_shape", cleaned_data.shape)
        
        # Feature engineering
        preprocessor.feature_engineering()
        
        # Create visualizations
        preprocessor.create_visualizations()
        
        # Log artifacts
        mlflow.log_artifacts("plots", "visualizations")
        
        # Save processed data
        preprocessor.save_processed_data()
        mlflow.log_artifacts("processed_data", "processed_data")
        
        logger.info("Data preprocessing completed successfully!")

if __name__ == "__main__":
    main()
