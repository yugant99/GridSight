import streamlit as st
import pandas as pd
import json
import io
from azure.storage.blob import BlobServiceClient
from .azure_config import get_azure_config, get_containers
from datetime import datetime, timedelta

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data_from_azure(container_name, blob_name, file_type='csv'):
    """Load data from Azure Blob Storage with caching"""
    
    try:
        config = get_azure_config()
        blob_service_client = BlobServiceClient(
            account_url=f"https://{config['account_name']}.blob.core.windows.net",
            credential=config['account_key']
        )
        
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        
        # Download blob content
        blob_data = blob_client.download_blob().readall()
        
        if file_type == 'csv':
            return pd.read_csv(io.BytesIO(blob_data))
        elif file_type == 'json':
            return json.loads(blob_data.decode('utf-8'))
        else:
            return blob_data
            
    except Exception as e:
        st.error(f"Error loading {blob_name} from {container_name}: {str(e)}")
        return None

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def load_latest_predictions():
    """Load the latest ML predictions"""
    return load_data_from_azure("ml-outputs", "latest_predictions.json", "json")

@st.cache_data(ttl=1800)
def load_model_summary():
    """Load model performance summary"""
    return load_data_from_azure("ml-outputs", "model_summary.json", "json")

@st.cache_data(ttl=3600)
def get_available_data_files():
    """Get list of available data files in each container"""
    
    try:
        config = get_azure_config()
        blob_service_client = BlobServiceClient(
            account_url=f"https://{config['account_name']}.blob.core.windows.net",
            credential=config['account_key']
        )
        
        containers = get_containers()
        available_files = {}
        
        for container_type, container_name in containers.items():
            try:
                container_client = blob_service_client.get_container_client(container_name)
                blobs = list(container_client.list_blobs())
                available_files[container_type] = [blob.name for blob in blobs]
            except:
                available_files[container_type] = []
        
        return available_files
        
    except Exception as e:
        st.error(f"Error getting file list: {str(e)}")
        return {}

@st.cache_data(ttl=3600)
def load_demand_data():
    """Load all available demand data"""
    files = get_available_data_files()
    demand_files = [f for f in files.get('cleaned_data', []) if 'Demand' in f and f.endswith('.csv')]
    
    if not demand_files:
        return None
    
    # Load the most recent demand file
    latest_file = sorted(demand_files)[-1]
    return load_data_from_azure("cleaned-data", latest_file)

@st.cache_data(ttl=3600)
def load_genmix_data():
    """Load all available generation mix data"""
    files = get_available_data_files()
    genmix_files = [f for f in files.get('cleaned_data', []) if 'GenOutput' in f and f.endswith('.csv')]
    
    if not genmix_files:
        return None
    
    # Load the most recent genmix file
    latest_file = sorted(genmix_files)[-1]
    return load_data_from_azure("cleaned-data", latest_file)

@st.cache_data(ttl=3600)
def load_zonal_data():
    """Load zonal demand data if available"""
    files = get_available_data_files()
    zonal_files = [f for f in files.get('cleaned_data', []) if 'Zonal' in f and f.endswith('.csv')]
    
    if not zonal_files:
        return None
    
    # Load the most recent zonal file
    latest_file = sorted(zonal_files)[-1]
    return load_data_from_azure("cleaned-data", latest_file)

def refresh_cache():
    """Clear all cached data to force refresh"""
    st.cache_data.clear()
    st.success("✅ Cache refreshed! Data will be reloaded.") 