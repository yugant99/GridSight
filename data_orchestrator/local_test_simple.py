#!/usr/bin/env python3
"""
Simplified local testing for core ML functions
Tests only the ML components without Azure Functions decorators
"""

import os
import sys
import logging
from datetime import datetime

# Set up environment variables for testing
os.environ['AZURE_STORAGE_ACCOUNT_NAME'] = 'datastoreyugant'
os.environ['AZURE_STORAGE_ACCOUNT_KEY'] = 'YOUR_AZURE_STORAGE_KEY_HERE'  # Replace with your actual key

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_azure_connection():
    """Test connection to Azure blob storage"""
    try:
        from azure.storage.blob import BlobServiceClient
        
        account_name = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME')
        account_key = os.environ.get('AZURE_STORAGE_ACCOUNT_KEY')
        
        blob_client = BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net", 
            credential=account_key
        )
        
        # Test listing containers
        containers = list(blob_client.list_containers())
        container_names = [c.name for c in containers]
        
        logging.info(f"Azure connection successful!")
        logging.info(f"Found containers: {container_names}")
        
        return True
        
    except Exception as e:
        logging.error(f"Azure connection failed: {str(e)}")
        return False

def test_ml_functions():
    """Test the core ML functions"""
    try:
        import pandas as pd
        import numpy as np
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import mean_absolute_error, accuracy_score
        import xgboost as xgb
        
        logging.info("All ML libraries imported successfully")
        
        # Test basic functionality
        df = pd.DataFrame({
            'timestamp': pd.date_range('2025-01-01', periods=100, freq='5T'),
            'ontario_demand': np.random.normal(18000, 2000, 100),
            'output': np.random.normal(19000, 2000, 100)
        })
        
        # Test XGBoost
        X = df[['ontario_demand']].values
        y = df['output'].values
        
        model = xgb.XGBRegressor(n_estimators=10, random_state=42)
        model.fit(X, y)
        predictions = model.predict(X)
        mae = mean_absolute_error(y, predictions)
        
        logging.info(f"XGBoost test successful. MAE: {mae:.2f}")
        
        return True
        
    except Exception as e:
        logging.error(f"ML functions test failed: {str(e)}")
        return False

def main():
    """Run simplified tests"""
    logging.info("STARTING SIMPLIFIED ML TESTS")
    
    tests = [
        ("Azure Connection", test_azure_connection),
        ("ML Libraries", test_ml_functions)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logging.info(f"Running {test_name} test...")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                logging.info(f"{test_name} test PASSED")
            else:
                logging.error(f"{test_name} test FAILED")
        except Exception as e:
            logging.error(f"{test_name} test CRASHED: {str(e)}")
            results[test_name] = False
    
    passed = sum(results.values())
    total = len(results)
    
    if passed == total:
        logging.info("ALL TESTS PASSED - Ready for deployment!")
        return True
    else:
        logging.error("SOME TESTS FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 