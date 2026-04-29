#!/bin/bash

# PowerBI Data Analysis Setup Script
echo "Setting up PowerBI Data Analysis Environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating project directories..."
mkdir -p data models output logs powerbi_output notebooks/checkpoints

# Copy dataset if it exists
if [ -f "Dataset/Fish.csv" ]; then
    echo "Copying Fish dataset..."
    cp Dataset/Fish.csv data/
elif [ -f "data/Fish.csv" ]; then
    echo "Fish dataset already exists in data directory"
else
    echo "Warning: Fish.csv not found in Dataset/ or data/ directory"
fi

# Initialize Airflow database (if using Airflow)
if command -v airflow &> /dev/null; then
    echo "Initializing Airflow database..."
    export AIRFLOW_HOME=$(pwd)/Apache\ Airflow
    airflow db init
fi

# Set up environment variables
echo "Setting up environment variables..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# PowerBI Configuration
POWERBI_CLIENT_ID=your_client_id_here
POWERBI_CLIENT_SECRET=your_client_secret_here
POWERBI_TENANT_ID=your_tenant_id_here

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fish_analysis
DB_USER=airflow
DB_PASSWORD=airflow

# Airflow Configuration
AIRFLOW_HOME=$(pwd)/Apache Airflow
AIRFLOW__CORE__DAGS_FOLDER=$(pwd)/Apache Airflow
AIRFLOW__CORE__LOAD_EXAMPLES=False
EOF
fi

echo "Setup completed successfully!"
echo "To activate the environment, run: source venv/bin/activate"
echo "To start Jupyter notebook, run: jupyter notebook"
echo "To start Airflow webserver, run: cd 'Apache Airflow' && airflow webserver"