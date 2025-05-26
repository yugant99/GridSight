# Azure Storage Configuration Template
# Copy this file to config.py and fill in your actual credentials

ACCOUNT_NAME = "YOUR_AZURE_STORAGE_ACCOUNT_NAME"
ACCOUNT_KEY = "YOUR_AZURE_STORAGE_ACCOUNT_KEY"

# Container names
RAW_CONTAINER = "raw-data"
CLEANED_CONTAINER = "cleaned-data"

# Connection string
CONN_STR = f"DefaultEndpointsProtocol=https;AccountName={ACCOUNT_NAME};AccountKey={ACCOUNT_KEY};EndpointSuffix=core.windows.net" 