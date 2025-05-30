# Azure Storage Setup Guide

## Step 1: Get Your Azure Storage Key

1. **Go to Azure Portal**: https://portal.azure.com
2. **Navigate to Storage Accounts**: Search for "Storage Accounts" in the search bar
3. **Select your storage account**: `datastoreyugant`
4. **Go to Access Keys**: In the left sidebar, click "Security + networking" → "Access keys"
5. **Copy the key**: Copy either `key1` or `key2` (both work the same)

## Step 2: Configure the Key

### Option A: Using Streamlit Secrets (Recommended)
1. **Edit the secrets file**: Open `.streamlit/secrets.toml`
2. **Replace the placeholder**: Change `YOUR_AZURE_STORAGE_KEY_HERE` with your actual key
3. **Save the file**

### Option B: Using Environment Variable
```bash
export AZURE_STORAGE_ACCOUNT_KEY="your_actual_key_here"
```

## Step 3: Restart Streamlit
```bash
# Stop the current app (Ctrl+C)
# Then restart:
streamlit run main.py
```

## Security Note
- **Never commit** your actual Azure key to version control
- The `.streamlit/secrets.toml` file should be added to `.gitignore`
- Keep your keys secure and rotate them regularly

## Verification
Once configured correctly, you should see:
- ✅ "Connected to Azure" in the sidebar
- ✅ Data loading successfully from Azure Storage 