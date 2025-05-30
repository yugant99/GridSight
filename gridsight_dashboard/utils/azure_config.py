import os
import streamlit as st

def get_azure_config():
    """Get Azure configuration from environment variables or Streamlit secrets"""
    
    # Try to get from Streamlit secrets first (for deployed app)
    try:
        account_name = st.secrets["azure"]["account_name"]
        account_key = st.secrets["azure"]["account_key"]
    except:
        # Fallback to environment variables (for local development)
        account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME', 'datastoreyugant')
        account_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY', '')
        
        # If still no key, prompt user to add it
        if not account_key:
            st.error("❌ Azure Storage Key not found!")
            st.info("Please add your Azure Storage Key:")
            st.code("""
# Option 1: Environment Variable
export AZURE_STORAGE_ACCOUNT_KEY="your_key_here"

# Option 2: Streamlit Secrets (for deployment)
# Create .streamlit/secrets.toml:
[azure]
account_name = "datastoreyugant"
account_key = "your_key_here"
            """)
            st.stop()
    
    return {
        "account_name": account_name,
        "account_key": account_key,
        "connection_string": f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
    }

def get_containers():
    """Return the list of containers we'll be accessing"""
    return {
        "raw_data": "raw-data",
        "cleaned_data": "cleaned-data", 
        "ml_outputs": "ml-outputs"
    } 