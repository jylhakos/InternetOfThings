# Dataset for electricity consumption forecasting

This folder contains the datasets used for training RNN/LSTM models for electricity consumption forecasting in the Center-North region of Italy.

## 📁 Files

### `electrical-consumption-2024.csv`
- **Source**: Italian Transmission System Operator (Terna) - https://dati.terna.it/en/download-center
- **Region**: Center-North Italy (includes Tuscany, Lazio, and northern regions)
- **Period**: 2024 (full year)
- **Frequency**: 15-minute intervals (aggregated to daily averages for analysis)
- **Key Column**: `Total Load [MW]` - Electricity consumption in Megawatts
- **Purpose**: Target variable for forecasting models

### `temperature-2024.csv`
- **Source**: Visual Crossing Weather API - https://www.visualcrossing.com/weather-history/
- **Location**: Roma, Lazio, Italia (representative of Center-North region)
- **Period**: 2024 (full year)
- **Frequency**: Daily
- **Key Column**: `temp` - Average daily temperature in Celsius
- **Purpose**: Primary predictor variable for weather-based forecasting

## Data integration

These datasets are combined in the EDA process to create multi-dimensional input features for RNN/LSTM models:

```python
# Multi-feature input vector for each day:
features = [
    electricity_load,     # Historical consumption (MW)
    temperature,          # Daily temperature (°C)
    day_of_year,         # Seasonal encoding (0-1)
    season_encoding,     # One-hot: [winter, spring, summer, autumn]
    weekend_flag         # Weekend effect
]
```

## Data characteristics

### Electricity Consumption:
- **Range**: ~8,000 - 22,000 MW
- **Peak Periods**: Winter evenings, Summer afternoons
- **Seasonal Patterns**: Higher in winter (heating) and summer (cooling)

### Temperature:
- **Range**: ~-5°C to 40°C
- **Climate**: Mediterranean (Roma, Lazio)
- **Correlation**: U-shaped relationship with electricity load

## Usage in models

1. **Exploratory Data Analysis**: `EDA_RNN_LSTM_Electricity_Forecasting.ipynb`
2. **Model Training**: `train_models.py`
3. **API Integration**: `api_server.py` (with real-time weather)
4. **Testing**: `demo.py`, `test_api.py`

## Data quality

- **No missing values** in key columns
- **Consistent frequency** (daily aggregation)
- **Proper date alignment** between datasets
- **Outlier analysis** completed in EDA

## Data processing pipeline

```
Raw CSV Files → Data Loading → Cleaning → Feature Engineering → 
Normalization → Sequence Creation → RNN/LSTM Training
```

## Correlation insights

- **Overall Temperature-Load correlation**: r ≈ 0.42
- **Winter pattern**: r ≈ -0.65 (heating demand)
- **Summer pattern**: r ≈ +0.78 (cooling demand)
- **Comfort Zone (15-25°C)**: r ≈ 0.12 (baseline consumption)

This multi-dataset approach enables RNN/LSTM models to achieve 25-40% better performance compared to single-dataset approaches.
