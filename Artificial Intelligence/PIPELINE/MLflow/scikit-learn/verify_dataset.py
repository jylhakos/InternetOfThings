"""
Fish dataset verification script
===============================

This script verifies the Fish.csv dataset without requiring
machine learning libraries. Use this to check your data
before running the ML examples.

Author: Fish ML
Date: 2025
"""

import csv
import os
from collections import Counter

def verify_dataset():
    """Verify the Fish.csv dataset structure and content."""
    print("🐟 Fish Dataset Verification")
    print("=" * 40)
    
    dataset_path = "Dataset/Fish.csv"
    
    # Check if file exists
    if not os.path.exists(dataset_path):
        print(f"❌ Error: {dataset_path} not found!")
        print("Please ensure the Fish.csv file is in the Dataset/ folder.")
        return False
    
    print(f"✅ Dataset file found: {dataset_path}")
    
    try:
        # Read and analyze the CSV file
        with open(dataset_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Get column names
            columns = reader.fieldnames
            print(f"✅ Columns found: {columns}")
            
            # Expected columns
            expected_columns = ['Species', 'Weight', 'Length1', 'Length2', 'Length3', 'Height', 'Width']
            
            # Check if all expected columns are present
            missing_columns = set(expected_columns) - set(columns)
            if missing_columns:
                print(f"❌ Missing columns: {missing_columns}")
                return False
            else:
                print("✅ All expected columns present")
            
            # Read all rows and analyze data
            rows = list(reader)
            total_rows = len(rows)
            
            print(f"✅ Total samples: {total_rows}")
            
            if total_rows == 0:
                print("❌ No data found in the file!")
                return False
            
            # Analyze species distribution
            species_list = [row['Species'] for row in rows]
            species_counts = Counter(species_list)
            unique_species = len(species_counts)
            
            print(f"✅ Unique species: {unique_species}")
            print("\n📊 Species distribution:")
            for species, count in species_counts.most_common():
                percentage = (count / total_rows) * 100
                print(f"   {species:<12}: {count:>3} samples ({percentage:>5.1f}%)")
            
            # Check for missing values
            missing_data = False
            for i, row in enumerate(rows[:10]):  # Check first 10 rows
                for col in expected_columns:
                    if not row[col] or row[col].strip() == '':
                        print(f"❌ Missing value in row {i+1}, column '{col}'")
                        missing_data = True
                        break
                if missing_data:
                    break
            
            if not missing_data:
                print("✅ No missing values detected (checked first 10 rows)")
            
            # Check numeric data validity
            numeric_columns = ['Weight', 'Length1', 'Length2', 'Length3', 'Height', 'Width']
            numeric_valid = True
            
            for i, row in enumerate(rows[:5]):  # Check first 5 rows
                for col in numeric_columns:
                    try:
                        float(row[col])
                    except ValueError:
                        print(f"❌ Invalid numeric value '{row[col]}' in row {i+1}, column '{col}'")
                        numeric_valid = False
                        break
                if not numeric_valid:
                    break
            
            if numeric_valid:
                print("✅ Numeric data format valid (checked first 5 rows)")
            
            # Show sample data
            print(f"\n📋 Sample data (first 3 rows):")
            print("-" * 70)
            for i, row in enumerate(rows[:3]):
                print(f"Row {i+1}:")
                for col in expected_columns:
                    value = row[col]
                    if col in numeric_columns:
                        try:
                            value = f"{float(value):.2f}"
                        except:
                            pass
                    print(f"   {col:<10}: {value}")
                print()
            
            # Summary statistics for weight
            weights = []
            for row in rows:
                try:
                    weights.append(float(row['Weight']))
                except ValueError:
                    continue
            
            if weights:
                print(f"📈 Weight statistics:")
                print(f"   Min weight: {min(weights):.1f}g")
                print(f"   Max weight: {max(weights):.1f}g")
                print(f"   Avg weight: {sum(weights)/len(weights):.1f}g")
            
            return True
            
    except Exception as e:
        print(f"❌ Error reading dataset: {e}")
        return False

def show_next_steps():
    """Show what to do next."""
    print("\n" + "=" * 50)
    print("🚀 NEXT STEPS")
    print("=" * 50)
    print()
    print("Your dataset is ready! Here's what to do next:")
    print()
    print("1. 📦 Set up Python environment:")
    print("   ./setup.sh")
    print("   # OR manually:")
    print("   python3 -m venv venv")
    print("   source venv/bin/activate")
    print("   pip install -r requirements.txt")
    print()
    print("2. 🎯 Run machine learning examples:")
    print("   python fish_regression.py      # Weight prediction")
    print("   python fish_classification.py  # Species classification") 
    print("   python fish_analysis.py        # Comprehensive analysis")
    print()
    print("3. 📊 Start interactive analysis:")
    print("   jupyter notebook")
    print()
    print("4. 📖 Read the documentation:")
    print("   cat README.md")
    print()

def main():
    """Main verification function."""
    success = verify_dataset()
    
    if success:
        print("\n" + "="*40)
        print("✅ DATASET VERIFICATION SUCCESSFUL!")
        print("="*40)
        show_next_steps()
    else:
        print("\n" + "="*40)
        print("❌ DATASET VERIFICATION FAILED!")
        print("="*40)
        print("\nPlease check your dataset and try again.")
        print("Ensure Fish.csv is properly formatted and in the Dataset/ folder.")
    
    return success

if __name__ == "__main__":
    main()
