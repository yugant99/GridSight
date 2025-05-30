import os
import streamlit as st

def get_azure_config():
    """Get Azure configuration from environment variables or Streamlit secrets"""
    
    account_name = None
    account_key = None
    
    # Try to get from Streamlit secrets first (for deployed app)
    try:
        if hasattr(st, 'secrets') and 'azure' in st.secrets:
            account_name = st.secrets["azure"]["account_name"]
            account_key = st.secrets["azure"]["account_key"]
            st.sidebar.success("🔐 Using Streamlit secrets")
        else:
            st.sidebar.info("📝 No Streamlit secrets found")
    except Exception as e:
        st.sidebar.warning(f"⚠️ Secrets error: {str(e)}")
    
    # Fallback to environment variables (for local development)
    if not account_key:
        account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME', 'datastoreyugant')
        account_key = os.getenv('AZURE_STORAGE_ACCOUNT_KEY', '')
        
        if account_key:
            st.sidebar.success("🔐 Using environment variables")
        else:
            st.sidebar.error("❌ No Azure credentials found")
    
    # Debug information
    st.sidebar.write(f"**Account Name:** {account_name}")
    st.sidebar.write(f"**Key Status:** {'✅ Found' if account_key else '❌ Missing'}")
    
    # If still no key, show detailed error
    if not account_key:
        st.error("❌ Azure Storage Key not found!")
        st.info("**Debugging Information:**")
        
        # Check what's available
        try:
            if hasattr(st, 'secrets'):
                st.write("Streamlit secrets object exists")
                if 'azure' in st.secrets:
                    st.write("Azure section found in secrets")
                    st.write(f"Available keys: {list(st.secrets['azure'].keys())}")
                else:
                    st.write("❌ No 'azure' section in secrets")
                    st.write(f"Available sections: {list(st.secrets.keys())}")
            else:
                st.write("❌ No streamlit secrets object")
        except Exception as e:
            st.write(f"Error checking secrets: {e}")
        
        st.info("**Setup Instructions:**")
        st.code("""
# For Streamlit Cloud Deployment:
# 1. Go to your app settings
# 2. Click on "Secrets" tab
# 3. Add exactly this content:

[azure]
account_name = "datastoreyugant"
account_key = "YOUR_AZURE_STORAGE_KEY_HERE"

# For Local Development:
export AZURE_STORAGE_ACCOUNT_KEY="YOUR_AZURE_STORAGE_KEY_HERE"
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