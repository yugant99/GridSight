# Configuration Template for GridSight
# Copy this file to 'config.py' and fill in your Azure credentials

# Azure Storage Configuration
ACCOUNT_NAME = "your_storage_account_name"
ACCOUNT_KEY = "your_storage_account_key"

# Container Names
RAW_CONTAINER = "raw-data"
CLEANED_CONTAINER = "cleaned-data"

# Connection String (alternative to account name/key)
# AZURE_STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net" 