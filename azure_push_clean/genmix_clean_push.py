from azure.storage.blob import BlobClient
import os

# === config ===
conn_str = "DefaultEndpointsProtocol=https;AccountName=YOUR_AZURE_STORAGE_ACCOUNT;AccountKey=YOUR_AZURE_STORAGE_KEY_HERE;EndpointSuffix=core.windows.net"
local_path = "/Users/yuganthareshsoni/project_tester_1/call_azure_cleanstep1/Azure_clean_notpushed/PUB_GenOutputbyFuelHourly_2025_v139_cleaned.csv"
container_name = "cleaned-data"
blob_path = "GenMix/year=2025/PUB_GenOutputbyFuelHourly_2025_v139_cleaned.csv"

# === upload ===
def upload_to_azure(local_file, blob_path, container):
    blob = BlobClient.from_connection_string(
        conn_str, container_name=container, blob_name=blob_path
    )
    with open(local_file, "rb") as f:
        blob.upload_blob(f, overwrite=True)
    print(f"✅ Uploaded: {local_file} → {container}/{blob_path}")

# === verify file exists locally ===
if os.path.exists(local_path):
    print(f"📁 Found local file: {local_path}")
    file_size = os.path.getsize(local_path) / 1024  # KB
    print(f"📊 File size: {file_size:.1f} KB")
    
    upload_to_azure(local_path, blob_path, container_name)
else:
    print(f"❌ File not found: {local_path}") 