import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

class ElectricityDataAnalyzer:
    """
    Exploratory Data Analysis for Electricity Consumption and Temperature Data
    """
    
    def __init__(self):
        self.electricity_df = None
        self.temperature_df = None
        self.merged_df = None
        
    def load_data(self, electricity_path, temperature_path):
        """
        Load electricity consumption and temperature data
        """
        print("Loading electricity consumption data...")
        # Load electricity data
        self.electricity_df = pd.read_csv(electricity_path)
        self.electricity_df['Date'] = pd.to_datetime(self.electricity_df['Date'], format='%d/%m/%Y %H:%M:%S')
        self.electricity_df = self.electricity_df.sort_values('Date')
        
        print("Loading temperature data...")
        # Load temperature data
        self.temperature_df = pd.read_csv(temperature_path)
        self.temperature_df['datetime'] = pd.to_datetime(self.temperature_df['datetime'])
        
        # Data summary
        print(f"\nElectricity Data:")
        print(f"- Records: {len(self.electricity_df)}")
        print(f"- Date range: {self.electricity_df['Date'].min()} to {self.electricity_df['Date'].max()}")
        print(f"- Frequency: 15-minute intervals")
        
        print(f"\nTemperature Data:")
        print(f"- Records: {len(self.temperature_df)}")
        print(f"- Date range: {self.temperature_df['datetime'].min()} to {self.temperature_df['datetime'].max()}")
        print(f"- Frequency: Daily")
        
        return self.electricity_df, self.temperature_df
    
    def preprocess_data(self):
        """
        Preprocess and merge the datasets
        """
        # Aggregate electricity data to daily level
        electricity_daily = self.electricity_df.groupby(self.electricity_df['Date'].dt.date).agg({
            'Total Load [MW]': ['mean', 'min', 'max', 'std']
        }).reset_index()
        
        # Flatten column names
        electricity_daily.columns = ['Date', 'Load_Mean', 'Load_Min', 'Load_Max', 'Load_Std']
        electricity_daily['Date'] = pd.to_datetime(electricity_daily['Date'])
        
        # Prepare temperature data
        temp_daily = self.temperature_df[['datetime', 'temp', 'tempmin', 'tempmax', 'humidity']].copy()
        temp_daily = temp_daily.rename(columns={'datetime': 'Date'})
        
        # Merge datasets
        self.merged_df = pd.merge(electricity_daily, temp_daily, on='Date', how='inner')
        self.merged_df = self.merged_df.sort_values('Date').reset_index(drop=True)
        
        # Add time-based features
        self.merged_df['DayOfWeek'] = self.merged_df['Date'].dt.dayofweek
        self.merged_df['Month'] = self.merged_df['Date'].dt.month
        self.merged_df['DayOfYear'] = self.merged_df['Date'].dt.dayofyear
        self.merged_df['Quarter'] = self.merged_df['Date'].dt.quarter
        
        # Add season
        self.merged_df['Season'] = self.merged_df['Month'].apply(self._get_season_name)
        
        # Add weekend indicator
        self.merged_df['IsWeekend'] = self.merged_df['DayOfWeek'].apply(lambda x: 1 if x >= 5 else 0)
        
        print(f"\nMerged Dataset:")
        print(f"- Records: {len(self.merged_df)}")
        print(f"- Date range: {self.merged_df['Date'].min()} to {self.merged_df['Date'].max()}")
        
        return self.merged_df
    
    def _get_season_name(self, month):
        """Get season name from month"""
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Autumn'
    
    def basic_statistics(self):
        """
        Display basic statistics of the dataset
        """
        print("\n" + "="*60)
        print("BASIC STATISTICS")
        print("="*60)
        
        # Electricity consumption statistics
        print("\nElectricity Consumption Statistics (MW):")
        print("-" * 40)
        elec_stats = self.merged_df[['Load_Mean', 'Load_Min', 'Load_Max', 'Load_Std']].describe()
        print(elec_stats.round(2))
        
        # Temperature statistics
        print("\nTemperature Statistics (°C):")
        print("-" * 30)
        temp_stats = self.merged_df[['temp', 'tempmin', 'tempmax', 'humidity']].describe()
        print(temp_stats.round(2))
        
        # Seasonal statistics
        print("\nSeasonal Electricity Consumption (MW):")
        print("-" * 40)
        seasonal_stats = self.merged_df.groupby('Season')['Load_Mean'].agg(['mean', 'std', 'min', 'max'])
        print(seasonal_stats.round(2))
        
        return elec_stats, temp_stats, seasonal_stats
    
    def correlation_analysis(self):
        """
        Analyze correlation between variables
        """
        print("\n" + "="*60)
        print("CORRELATION ANALYSIS")
        print("="*60)
        
        # Select numerical columns for correlation
        corr_columns = ['Load_Mean', 'temp', 'tempmin', 'tempmax', 'humidity', 'DayOfYear', 'Month']
        correlation_matrix = self.merged_df[corr_columns].corr()
        
        # Display correlation with electricity load
        load_corr = correlation_matrix['Load_Mean'].sort_values(ascending=False)
        print("\nCorrelation with Electricity Load:")
        print("-" * 35)
        for var, corr in load_corr.items():
            if var != 'Load_Mean':
                print(f"{var:15s}: {corr:6.3f}")
        
        # Statistical significance
        print("\nStatistical Significance (p-values):")
        print("-" * 35)
        for col in corr_columns:
            if col != 'Load_Mean':
                corr_coef, p_value = pearsonr(self.merged_df['Load_Mean'], self.merged_df[col])
                significance = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else ""
                print(f"{col:15s}: p={p_value:6.3f} {significance}")
        
        return correlation_matrix
    
    def create_visualizations(self):
        """
        Create comprehensive visualizations
        """
        print("\n" + "="*60)
        print("CREATING VISUALIZATIONS")
        print("="*60)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        
        # 1. Time Series Plot
        fig, axes = plt.subplots(2, 1, figsize=(15, 10))
        
        # Electricity consumption over time
        axes[0].plot(self.merged_df['Date'], self.merged_df['Load_Mean'], color='blue', linewidth=1)
        axes[0].set_title('Daily Electricity Consumption (Center-North Italy, 2024)', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Electricity Load (MW)')
        axes[0].grid(True, alpha=0.3)
        
        # Temperature over time
        axes[1].plot(self.merged_df['Date'], self.merged_df['temp'], color='red', linewidth=1)
        axes[1].set_title('Daily Temperature (Roma, Lazio, 2024)', fontsize=14, fontweight='bold')
        axes[1].set_ylabel('Temperature (°C)')
        axes[1].set_xlabel('Date')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('time_series_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 2. Seasonal Analysis
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Electricity by season
        seasonal_load = self.merged_df.groupby('Season')['Load_Mean'].mean().sort_values(ascending=False)
        axes[0, 0].bar(seasonal_load.index, seasonal_load.values, color=['skyblue', 'lightgreen', 'orange', 'lightcoral'])
        axes[0, 0].set_title('Average Electricity Consumption by Season')
        axes[0, 0].set_ylabel('Average Load (MW)')
        
        # Temperature by season
        seasonal_temp = self.merged_df.groupby('Season')['temp'].mean().sort_values(ascending=False)
        axes[0, 1].bar(seasonal_temp.index, seasonal_temp.values, color=['red', 'orange', 'green', 'blue'])
        axes[0, 1].set_title('Average Temperature by Season')
        axes[0, 1].set_ylabel('Average Temperature (°C)')
        
        # Monthly patterns
        monthly_load = self.merged_df.groupby('Month')['Load_Mean'].mean()
        axes[1, 0].plot(monthly_load.index, monthly_load.values, marker='o', linewidth=2)
        axes[1, 0].set_title('Monthly Electricity Consumption Pattern')
        axes[1, 0].set_ylabel('Average Load (MW)')
        axes[1, 0].set_xlabel('Month')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Weekday vs Weekend
        weekend_analysis = self.merged_df.groupby('IsWeekend')['Load_Mean'].mean()
        labels = ['Weekdays', 'Weekends']
        axes[1, 1].bar(labels, weekend_analysis.values, color=['lightblue', 'lightgreen'])
        axes[1, 1].set_title('Electricity Consumption: Weekdays vs Weekends')
        axes[1, 1].set_ylabel('Average Load (MW)')
        
        plt.tight_layout()
        plt.savefig('seasonal_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 3. Correlation Heatmap
        plt.figure(figsize=(10, 8))
        corr_columns = ['Load_Mean', 'temp', 'tempmin', 'tempmax', 'humidity', 'DayOfYear']
        correlation_matrix = self.merged_df[corr_columns].corr()
        
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, linewidths=0.5, fmt='.3f')
        plt.title('Correlation Matrix: Electricity Load vs Weather Variables', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 4. Load vs Temperature Scatter Plot
        plt.figure(figsize=(12, 5))
        
        # Overall scatter
        plt.subplot(1, 2, 1)
        plt.scatter(self.merged_df['temp'], self.merged_df['Load_Mean'], alpha=0.6, s=20)
        plt.xlabel('Temperature (°C)')
        plt.ylabel('Electricity Load (MW)')
        plt.title('Electricity Load vs Temperature')
        plt.grid(True, alpha=0.3)
        
        # Add trend line
        z = np.polyfit(self.merged_df['temp'], self.merged_df['Load_Mean'], 1)
        p = np.poly1d(z)
        plt.plot(self.merged_df['temp'], p(self.merged_df['temp']), "r--", alpha=0.8)
        
        # Seasonal scatter
        plt.subplot(1, 2, 2)
        seasons = self.merged_df['Season'].unique()
        colors = ['blue', 'green', 'red', 'orange']
        for season, color in zip(seasons, colors):
            season_data = self.merged_df[self.merged_df['Season'] == season]
            plt.scatter(season_data['temp'], season_data['Load_Mean'], 
                       label=season, alpha=0.6, s=20, c=color)
        
        plt.xlabel('Temperature (°C)')
        plt.ylabel('Electricity Load (MW)')
        plt.title('Electricity Load vs Temperature by Season')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('load_temperature_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # 5. Distribution plots
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # Load distribution
        axes[0, 0].hist(self.merged_df['Load_Mean'], bins=30, color='skyblue', alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('Distribution of Electricity Load')
        axes[0, 0].set_xlabel('Load (MW)')
        axes[0, 0].set_ylabel('Frequency')
        
        # Temperature distribution
        axes[0, 1].hist(self.merged_df['temp'], bins=30, color='lightcoral', alpha=0.7, edgecolor='black')
        axes[0, 1].set_title('Distribution of Temperature')
        axes[0, 1].set_xlabel('Temperature (°C)')
        axes[0, 1].set_ylabel('Frequency')
        
        # Box plot by season - Load
        self.merged_df.boxplot(column='Load_Mean', by='Season', ax=axes[1, 0])
        axes[1, 0].set_title('Electricity Load Distribution by Season')
        axes[1, 0].set_xlabel('Season')
        axes[1, 0].set_ylabel('Load (MW)')
        
        # Box plot by season - Temperature
        self.merged_df.boxplot(column='temp', by='Season', ax=axes[1, 1])
        axes[1, 1].set_title('Temperature Distribution by Season')
        axes[1, 1].set_xlabel('Season')
        axes[1, 1].set_ylabel('Temperature (°C)')
        
        plt.suptitle('')  # Remove automatic title
        plt.tight_layout()
        plt.savefig('distribution_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("All visualizations saved as PNG files!")
    
    def create_interactive_plots(self):
        """
        Create interactive plots using Plotly
        """
        print("\nCreating interactive plots...")
        
        # 1. Interactive time series
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Electricity Consumption', 'Temperature'),
            vertical_spacing=0.1
        )
        
        # Add electricity load
        fig.add_trace(
            go.Scatter(x=self.merged_df['Date'], y=self.merged_df['Load_Mean'],
                      mode='lines', name='Electricity Load (MW)',
                      line=dict(color='blue', width=1)),
            row=1, col=1
        )
        
        # Add temperature
        fig.add_trace(
            go.Scatter(x=self.merged_df['Date'], y=self.merged_df['temp'],
                      mode='lines', name='Temperature (°C)',
                      line=dict(color='red', width=1)),
            row=2, col=1
        )
        
        fig.update_layout(
            title="Interactive Time Series: Electricity Consumption and Temperature (2024)",
            height=600,
            showlegend=True
        )
        
        fig.write_html("interactive_time_series.html")
        
        # 2. Interactive scatter plot
        fig2 = px.scatter(
            self.merged_df, 
            x='temp', 
            y='Load_Mean',
            color='Season',
            size='humidity',
            hover_data=['Date', 'tempmin', 'tempmax'],
            title="Electricity Load vs Temperature (Interactive)",
            labels={'temp': 'Temperature (°C)', 'Load_Mean': 'Electricity Load (MW)'}
        )
        
        fig2.write_html("interactive_scatter.html")
        
        print("Interactive plots saved as HTML files!")
    
    def generate_insights(self):
        """
        Generate key insights from the analysis
        """
        print("\n" + "="*60)
        print("KEY INSIGHTS")
        print("="*60)
        
        # Correlation insights
        temp_corr = self.merged_df['Load_Mean'].corr(self.merged_df['temp'])
        
        # Seasonal insights
        seasonal_avg = self.merged_df.groupby('Season')['Load_Mean'].mean()
        highest_season = seasonal_avg.idxmax()
        lowest_season = seasonal_avg.idxmin()
        
        # Weekend vs weekday
        weekend_avg = self.merged_df[self.merged_df['IsWeekend'] == 1]['Load_Mean'].mean()
        weekday_avg = self.merged_df[self.merged_df['IsWeekend'] == 0]['Load_Mean'].mean()
        
        # Temperature extremes
        hot_days = self.merged_df[self.merged_df['temp'] > 25]
        cold_days = self.merged_df[self.merged_df['temp'] < 5]
        
        print(f"1. TEMPERATURE-LOAD RELATIONSHIP:")
        print(f"   • Correlation coefficient: {temp_corr:.3f}")
        if abs(temp_corr) > 0.5:
            relationship = "strong" if abs(temp_corr) > 0.7 else "moderate"
            direction = "positive" if temp_corr > 0 else "negative"
            print(f"   • {relationship.capitalize()} {direction} correlation found")
        else:
            print(f"   • Weak correlation between temperature and electricity load")
        
        print(f"\n2. SEASONAL PATTERNS:")
        print(f"   • Highest consumption: {highest_season} ({seasonal_avg[highest_season]:.0f} MW)")
        print(f"   • Lowest consumption: {lowest_season} ({seasonal_avg[lowest_season]:.0f} MW)")
        print(f"   • Seasonal variation: {seasonal_avg.max() - seasonal_avg.min():.0f} MW")
        
        print(f"\n3. WEEKDAY vs WEEKEND:")
        print(f"   • Weekday average: {weekday_avg:.0f} MW")
        print(f"   • Weekend average: {weekend_avg:.0f} MW")
        print(f"   • Difference: {abs(weekday_avg - weekend_avg):.0f} MW")
        
        print(f"\n4. EXTREME WEATHER IMPACT:")
        if len(hot_days) > 0:
            print(f"   • Hot days (>25°C): {len(hot_days)} days, avg load: {hot_days['Load_Mean'].mean():.0f} MW")
        if len(cold_days) > 0:
            print(f"   • Cold days (<5°C): {len(cold_days)} days, avg load: {cold_days['Load_Mean'].mean():.0f} MW")
        
        print(f"\n5. DATA QUALITY:")
        print(f"   • Total days analyzed: {len(self.merged_df)}")
        print(f"   • Missing data points: {self.merged_df.isnull().sum().sum()}")
        print(f"   • Data completeness: {(1 - self.merged_df.isnull().sum().sum() / (len(self.merged_df) * len(self.merged_df.columns))) * 100:.1f}%")
        
        return {
            'temperature_correlation': temp_corr,
            'seasonal_patterns': seasonal_avg.to_dict(),
            'weekend_effect': weekend_avg - weekday_avg,
            'data_quality': len(self.merged_df)
        }

def main():
    """
    Main function to run the complete EDA
    """
    print("ELECTRICITY CONSUMPTION EXPLORATORY DATA ANALYSIS")
    print("=" * 60)
    print("Center-North Italy Electricity Demand Analysis")
    print("Dataset: 2024 Electricity Consumption and Weather Data")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = ElectricityDataAnalyzer()
    
    # Load data
    electricity_df, temperature_df = analyzer.load_data(
        'Dataset/electrical-consumption-2024.csv',
        'Dataset/temperature-2024.csv'
    )
    
    # Preprocess data
    merged_df = analyzer.preprocess_data()
    
    # Basic statistics
    elec_stats, temp_stats, seasonal_stats = analyzer.basic_statistics()
    
    # Correlation analysis
    correlation_matrix = analyzer.correlation_analysis()
    
    # Create visualizations
    analyzer.create_visualizations()
    
    # Create interactive plots
    analyzer.create_interactive_plots()
    
    # Generate insights
    insights = analyzer.generate_insights()
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE!")
    print("="*60)
    print("Generated files:")
    print("• time_series_analysis.png")
    print("• seasonal_analysis.png") 
    print("• correlation_heatmap.png")
    print("• load_temperature_analysis.png")
    print("• distribution_analysis.png")
    print("• interactive_time_series.html")
    print("• interactive_scatter.html")

if __name__ == "__main__":
    main()
