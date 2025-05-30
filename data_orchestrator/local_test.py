#!/usr/bin/env python3
"""
Local testing script for ML Orchestrator
Tests the orchestrator functions locally before Azure deployment
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
        from function_app import get_blob_service_client
        
        blob_client = get_blob_service_client()
        
        # Test listing containers
        containers = list(blob_client.list_containers())
        container_names = [c.name for c in containers]
        
        logging.info(f"✅ Azure connection successful!")
        logging.info(f"Found containers: {container_names}")
        
        # Check for required containers
        required_containers = ['raw-data', 'cleaned-data']
        for container in required_containers:
            if container in container_names:
                logging.info(f"✅ Required container '{container}' found")
            else:
                logging.warning(f"⚠️ Required container '{container}' not found")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Azure connection failed: {str(e)}")
        return False

def test_data_loading():
    """Test loading data from Azure blob storage"""
    try:
        from function_app import read_blob_to_dataframe
        
        # Try to load demand data
        demand_files = [
            "Demand/PUB_Demand_2025_v144_cleaned.csv",
            "Demand/PUB_Demand_2025_v148_cleaned.csv"
        ]
        
        demand_df = None
        for filename in demand_files:
            try:
                demand_df = read_blob_to_dataframe("cleaned-data", filename)
                logging.info(f"✅ Successfully loaded demand data from {filename}")
                logging.info(f"   Shape: {demand_df.shape}")
                logging.info(f"   Columns: {list(demand_df.columns)}")
                break
            except Exception as e:
                logging.warning(f"⚠️ Could not load {filename}: {str(e)}")
                continue
        
        if demand_df is None:
            logging.error("❌ Could not load any demand data")
            return False
        
        # Try to load genmix data
        genmix_files = [
            "GenMix/PUB_GenOutputbyFuelHourly_2025_v144_cleaned.csv",
            "GenMix/PUB_GenOutputbyFuelHourly_2025_v148_cleaned.csv"
        ]
        
        genmix_df = None
        for filename in genmix_files:
            try:
                genmix_df = read_blob_to_dataframe("cleaned-data", filename)
                logging.info(f"✅ Successfully loaded genmix data from {filename}")
                logging.info(f"   Shape: {genmix_df.shape}")
                logging.info(f"   Columns: {list(genmix_df.columns)}")
                break
            except Exception as e:
                logging.warning(f"⚠️ Could not load {filename}: {str(e)}")
                continue
        
        if genmix_df is None:
            logging.error("❌ Could not load any genmix data")
            return False
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Data loading test failed: {str(e)}")
        return False

def test_model_training():
    """Test model training with sample data"""
    try:
        from function_app import (
            read_blob_to_dataframe, 
            train_demand_forecaster, 
            train_grid_stress_detector,
            generate_predictions
        )
        
        logging.info("Loading data for model training test...")
        
        # Load sample data
        demand_files = [
            "Demand/PUB_Demand_2025_v148_cleaned.csv",
            "Demand/PUB_Demand_2025_v144_cleaned.csv"
        ]
        
        demand_df = None
        for filename in demand_files:
            try:
                demand_df = read_blob_to_dataframe("cleaned-data", filename)
                break
            except:
                continue
        
        genmix_files = [
            "GenMix/PUB_GenOutputbyFuelHourly_2025_v148_cleaned.csv",
            "GenMix/PUB_GenOutputbyFuelHourly_2025_v144_cleaned.csv"
        ]
        
        genmix_df = None
        for filename in genmix_files:
            try:
                genmix_df = read_blob_to_dataframe("cleaned-data", filename)
                break
            except:
                continue
        
        if demand_df is None or genmix_df is None:
            logging.error("❌ Could not load required data for model training")
            return False
        
        # Test demand forecasting model
        logging.info("Testing demand forecasting model...")
        demand_model_info = train_demand_forecaster(demand_df)
        logging.info(f"✅ Demand model trained successfully. MAE: {demand_model_info['mae']:.2f}")
        
        # Test grid stress detection model
        logging.info("Testing grid stress detection model...")
        stress_model_info = train_grid_stress_detector(demand_df, genmix_df)
        logging.info(f"✅ Stress model trained successfully. Accuracy: {stress_model_info['accuracy']:.3f}")
        
        # Test prediction generation
        logging.info("Testing prediction generation...")
        predictions = generate_predictions(demand_model_info, stress_model_info, demand_df)
        logging.info(f"✅ Generated {len(predictions['forecast_24h'])} predictions")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Model training test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_blob_save():
    """Test saving results to blob storage"""
    try:
        from function_app import save_blob_from_string, get_blob_service_client
        import json
        
        # Create test data
        test_data = {
            "test_timestamp": datetime.now().isoformat(),
            "test_message": "ML Orchestrator local test successful"
        }
        
        test_json = json.dumps(test_data, indent=2)
        
        # Save to ml-outputs container
        blob_client = get_blob_service_client()
        try:
            blob_client.create_container("ml-outputs")
            logging.info("✅ Created ml-outputs container")
        except:
            logging.info("✅ ml-outputs container already exists")
        
        save_blob_from_string("ml-outputs", "local_test_results.json", test_json)
        logging.info("✅ Successfully saved test data to blob storage")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Blob save test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    logging.info("🧪 STARTING ML ORCHESTRATOR LOCAL TESTS")
    logging.info("=" * 60)
    
    tests = [
        ("Azure Connection", test_azure_connection),
        ("Data Loading", test_data_loading),
        ("Model Training", test_model_training),
        ("Blob Save", test_blob_save)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logging.info(f"\n🔍 Running {test_name} test...")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                logging.info(f"✅ {test_name} test PASSED")
            else:
                logging.error(f"❌ {test_name} test FAILED")
        except Exception as e:
            logging.error(f"❌ {test_name} test CRASHED: {str(e)}")
            results[test_name] = False
    
    logging.info("\n" + "=" * 60)
    logging.info("🏁 TEST SUMMARY")
    logging.info("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logging.info(f"{test_name}: {status}")
    
    logging.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logging.info("🎉 ALL TESTS PASSED - Ready for Azure deployment!")
        return True
    else:
        logging.error("❌ SOME TESTS FAILED - Fix issues before deploying")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 