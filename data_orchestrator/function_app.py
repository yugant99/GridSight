import azure.functions as func
import logging
import os
import sys
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from io import StringIO

# Azure SDK imports
from azure.storage.blob import BlobServiceClient

# ML imports  
import joblib
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, accuracy_score, classification_report
import xgboost as xgb

# Initialize Function App
app = func.FunctionApp()

def get_blob_service_client():
    """Get authenticated blob service client using environment variables"""
    account_name = os.environ.get('AZURE_STORAGE_ACCOUNT_NAME', 'datastoreyugant')
    account_key = os.environ.get('AZURE_STORAGE_ACCOUNT_KEY')
    
    if not account_key:
        raise ValueError("AZURE_STORAGE_ACCOUNT_KEY environment variable not set")
    
    return BlobServiceClient(
        account_url=f"https://{account_name}.blob.core.windows.net", 
        credential=account_key
    )

def read_blob_to_dataframe(container_name, blob_path):
    """Read CSV blob directly to pandas DataFrame"""
    try:
        blob_client = get_blob_service_client()
        container_client = blob_client.get_container_client(container_name)
        
        logging.info(f"Reading blob: {container_name}/{blob_path}")
        blob_data = container_client.download_blob(blob_path)
        csv_content = blob_data.readall().decode('utf-8')
        
        df = pd.read_csv(StringIO(csv_content))
        logging.info(f"Successfully loaded {len(df)} rows from {blob_path}")
        return df
        
    except Exception as e:
        logging.error(f"Error reading blob {blob_path}: {str(e)}")
        raise

def save_blob_from_string(container_name, blob_path, content):
    """Save string content to blob storage"""
    try:
        blob_client = get_blob_service_client()
        container_client = blob_client.get_container_client(container_name)
        
        logging.info(f"Saving blob: {container_name}/{blob_path}")
        container_client.upload_blob(blob_path, content, overwrite=True)
        logging.info(f"Successfully saved {blob_path}")
        
    except Exception as e:
        logging.error(f"Error saving blob {blob_path}: {str(e)}")
        raise

def prepare_demand_features(demand_df):
    """Feature engineering for demand forecasting"""
    df = demand_df.copy()
    
    # Ensure timestamp is datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Time-based features
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['month'] = df['timestamp'].dt.month
    df['day_of_year'] = df['timestamp'].dt.dayofyear
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    
    # Lag features (assuming hourly data, so 1 lag = 1 hour)
    df['demand_lag_1h'] = df['Ontario Demand'].shift(1)
    df['demand_lag_24h'] = df['Ontario Demand'].shift(24)  # 24 hours
    df['demand_lag_7d'] = df['Ontario Demand'].shift(24 * 7)  # 7 days
    
    # Rolling features
    df['demand_rolling_24h_mean'] = df['Ontario Demand'].rolling(window=24, min_periods=1).mean()
    df['demand_rolling_24h_std'] = df['Ontario Demand'].rolling(window=24, min_periods=1).std()
    
    # Drop rows with NaN values in critical features
    feature_cols = ['hour', 'day_of_week', 'month', 'demand_lag_1h', 'demand_lag_24h', 'Ontario Demand']
    df = df.dropna(subset=feature_cols)
    
    return df

def train_demand_forecaster(demand_df):
    """Train XGBoost demand forecasting model"""
    logging.info("Training demand forecasting model...")
    
    df = prepare_demand_features(demand_df)
    
    # Features for modeling
    feature_cols = [
        'hour', 'day_of_week', 'month', 'day_of_year', 'is_weekend',
        'demand_lag_1h', 'demand_lag_24h', 'demand_lag_7d',
        'demand_rolling_24h_mean', 'demand_rolling_24h_std'
    ]
    
    # Remove any remaining NaN rows
    df = df.dropna(subset=feature_cols + ['Ontario Demand'])
    
    X = df[feature_cols].fillna(0)  # Fill any remaining NaN with 0
    y = df['Ontario Demand']
    
    # Time series split for validation
    tscv = TimeSeriesSplit(n_splits=3)
    
    # Train XGBoost model
    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        n_jobs=-1
    )
    
    # Use the latest split for training
    train_idx, test_idx = list(tscv.split(X))[-1]
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    
    logging.info(f"Demand forecasting model trained. MAE: {mae:.2f} MW")
    
    # Feature importance
    importance = dict(zip(feature_cols, model.feature_importances_))
    
    return {
        'model': model,
        'feature_cols': feature_cols,
        'mae': mae,
        'importance': importance
    }

def prepare_grid_stress_features(demand_df, genmix_df):
    """Prepare features for grid stress detection"""
    logging.info("Preparing grid stress features...")
    
    # Convert timestamps
    demand_df['timestamp'] = pd.to_datetime(demand_df['timestamp'])
    genmix_df['timestamp'] = pd.to_datetime(genmix_df['timestamp'])
    
    # Aggregate generation by timestamp
    genmix_agg = genmix_df.groupby('timestamp')['output'].sum().reset_index()
    genmix_agg.columns = ['timestamp', 'total_generation']
    
    # Merge demand and generation
    df = pd.merge(demand_df[['timestamp', 'Ontario Demand']], genmix_agg, on='timestamp', how='inner')
    
    # Calculate features
    df['generation_demand_ratio'] = df['total_generation'] / df['Ontario Demand']
    df['reserve_margin'] = (df['total_generation'] - df['Ontario Demand']) / df['Ontario Demand']
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    
    # Define grid stress (reserve margin < 10%)
    df['is_stressed'] = (df['reserve_margin'] < 0.1).astype(int)
    
    return df

def train_grid_stress_detector(demand_df, genmix_df):
    """Train Random Forest grid stress detection model"""
    logging.info("Training grid stress detection model...")
    
    df = prepare_grid_stress_features(demand_df, genmix_df)
    
    feature_cols = [
        'Ontario Demand', 'total_generation', 'generation_demand_ratio', 
        'reserve_margin', 'hour', 'day_of_week'
    ]
    
    # Remove NaN rows
    df = df.dropna(subset=feature_cols + ['is_stressed'])
    
    X = df[feature_cols]
    y = df['is_stressed']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train Random Forest
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    logging.info(f"Grid stress detection model trained. Accuracy: {accuracy:.3f}")
    
    # Feature importance
    importance = dict(zip(feature_cols, model.feature_importances_))
    
    return {
        'model': model,
        'feature_cols': feature_cols,
        'accuracy': accuracy,
        'importance': importance
    }

def generate_predictions(demand_model_info, stress_model_info, latest_data):
    """Generate 24-hour forecasts and current grid status"""
    
    # Generate demand forecast for next 24 hours
    demand_model = demand_model_info['model']
    demand_features = demand_model_info['feature_cols']
    
    # Create prediction timestamps (next 24 hours, hourly intervals)
    last_timestamp = pd.to_datetime(latest_data['timestamp'].max())
    future_timestamps = pd.date_range(
        start=last_timestamp + timedelta(hours=1),
        end=last_timestamp + timedelta(hours=24),
        freq='1H'
    )
    
    predictions = []
    for ts in future_timestamps:
        # Create feature vector for this timestamp
        features = {
            'hour': ts.hour,
            'day_of_week': ts.dayofweek,
            'month': ts.month,
            'day_of_year': ts.dayofyear,
            'is_weekend': int(ts.dayofweek >= 5),
            'demand_lag_1h': float(latest_data['Ontario Demand'].iloc[-1]),
            'demand_lag_24h': float(latest_data['Ontario Demand'].iloc[-24]) if len(latest_data) >= 24 else float(latest_data['Ontario Demand'].iloc[0]),
            'demand_lag_7d': float(latest_data['Ontario Demand'].iloc[-24*7]) if len(latest_data) >= 24*7 else float(latest_data['Ontario Demand'].iloc[0]),
            'demand_rolling_24h_mean': float(latest_data['Ontario Demand'].iloc[-24:].mean()) if len(latest_data) >= 24 else float(latest_data['Ontario Demand'].mean()),
            'demand_rolling_24h_std': float(latest_data['Ontario Demand'].iloc[-24:].std()) if len(latest_data) >= 24 and not pd.isna(latest_data['Ontario Demand'].iloc[-24:].std()) else 0.0
        }
        
        # Make prediction
        feature_vector = np.array([[features[col] for col in demand_features]])
        predicted_demand = demand_model.predict(feature_vector)[0]
        
        predictions.append({
            'timestamp': ts.isoformat(),
            'predicted_demand': float(predicted_demand)
        })
    
    return {
        'forecast_24h': predictions,
        'model_performance': {
            'demand_mae': float(demand_model_info['mae']),
            'stress_accuracy': float(stress_model_info['accuracy'])
        },
        'generated_at': datetime.now().isoformat()
    }

@app.function_name(name="ml_orchestrator_timer")
@app.timer_trigger(schedule="0 0 14 * * *", arg_name="mytimer", run_on_startup=False, use_monitor=False)  
def ml_orchestrator_timer(mytimer: func.TimerRequest) -> None:
    """
    ML Orchestrator Function - Runs daily at 2 PM EST
    Trains models and generates predictions from Azure blob data
    """
    
    logging.info('ML Orchestrator starting...')
    
    try:
        # Load training data from cleaned-data container
        logging.info("Loading demand data...")
        demand_files = [
            "PUB_Demand_2025_v144_cleaned.csv",
            "PUB_Demand_2025_v148_cleaned.csv"  # Try both versions
        ]
        
        demand_df = None
        for filename in demand_files:
            try:
                demand_df = read_blob_to_dataframe("cleaned-data", f"Demand/{filename}")
                logging.info(f"Successfully loaded demand data from {filename}")
                break
            except Exception as e:
                logging.warning(f"Could not load {filename}: {str(e)}")
                continue
        
        if demand_df is None:
            raise Exception("Could not load any demand data files")
        
        logging.info("Loading generation mix data...")
        genmix_files = [
            "PUB_GenOutputbyFuelHourly_2025_v144_cleaned.csv",
            "PUB_GenOutputbyFuelHourly_2025_v148_cleaned.csv"
        ]
        
        genmix_df = None
        for filename in genmix_files:
            try:
                genmix_df = read_blob_to_dataframe("cleaned-data", f"GenMix/{filename}")
                logging.info(f"Successfully loaded genmix data from {filename}")
                break
            except Exception as e:
                logging.warning(f"Could not load {filename}: {str(e)}")
                continue
        
        if genmix_df is None:
            raise Exception("Could not load any generation mix data files")
        
        # Train models
        logging.info("Training demand forecasting model...")
        demand_model_info = train_demand_forecaster(demand_df)
        
        logging.info("Training grid stress detection model...")
        stress_model_info = train_grid_stress_detector(demand_df, genmix_df)
        
        # Generate predictions
        logging.info("Generating predictions...")
        predictions = generate_predictions(demand_model_info, stress_model_info, demand_df)
        
        # Save models and predictions to blob storage
        logging.info("Saving results to blob storage...")
        
        # Create ml-outputs container if it doesn't exist
        blob_client = get_blob_service_client()
        try:
            blob_client.create_container("ml-outputs")
        except:
            pass  # Container already exists
        
        # Save models as pickled bytes
        import pickle
        demand_model_bytes = pickle.dumps(demand_model_info)
        stress_model_bytes = pickle.dumps(stress_model_info)
        
        save_blob_from_string("ml-outputs", "demand_forecaster.pkl", demand_model_bytes)
        save_blob_from_string("ml-outputs", "stress_detector.pkl", stress_model_bytes)
        
        # Save predictions as JSON
        predictions_json = json.dumps(predictions, indent=2)
        save_blob_from_string("ml-outputs", "latest_predictions.json", predictions_json)
        
        # Save model summary
        model_summary = {
            "training_completed_at": datetime.now().isoformat(),
            "demand_model": {
                "mae": float(demand_model_info['mae']),
                "feature_importance": {k: float(v) for k, v in demand_model_info['importance'].items()}
            },
            "stress_model": {
                "accuracy": float(stress_model_info['accuracy']), 
                "feature_importance": {k: float(v) for k, v in stress_model_info['importance'].items()}
            },
            "data_sources": {
                "demand_records": len(demand_df),
                "genmix_records": len(genmix_df),
                "date_range": {
                    "start": str(demand_df['timestamp'].min()),
                    "end": str(demand_df['timestamp'].max())
                }
            }
        }
        
        summary_json = json.dumps(model_summary, indent=2)
        save_blob_from_string("ml-outputs", "model_summary.json", summary_json)
        
        logging.info("✅ ML Orchestrator completed successfully!")
        logging.info(f"Demand Model MAE: {demand_model_info['mae']:.2f} MW")
        logging.info(f"Stress Model Accuracy: {stress_model_info['accuracy']:.3f}")
        
    except Exception as e:
        logging.error(f"❌ ML Orchestrator failed: {str(e)}")
        raise

@app.function_name(name="health_check")
@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS)
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    return func.HttpResponse("ML Orchestrator is healthy", status_code=200)

@app.function_name(name="manual_trigger")
@app.route(route="trigger_ml", auth_level=func.AuthLevel.FUNCTION)
def manual_trigger(req: func.HttpRequest) -> func.HttpResponse:
    """Manual trigger for ML pipeline"""
    try:
        ml_orchestrator_timer(None)
        return func.HttpResponse("ML Pipeline completed successfully", status_code=200)
    except Exception as e:
        return func.HttpResponse(f"ML Pipeline failed: {str(e)}", status_code=500) 