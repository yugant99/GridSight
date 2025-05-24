from azure.storage.blob import BlobClient
import os

# === config ===
conn_str = "DefaultEndpointsProtocol=https;AccountName=YOUR_AZURE_STORAGE_ACCOUNT;AccountKey=YOUR_AZURE_STORAGE_KEY_HERE;EndpointSuffix=core.windows.net"
local_path = "/Users/yuganthareshsoni/project_tester_1/call_azure_cleanstep1/Azure_clean_notpushed/PUB_RealtimeDemandZonal_cleaned.csv"
container_name = "cleaned-data"
blob_path = "DemandZonal/year=2025/PUB_RealtimeDemandZonal_cleaned.csv"

# === upload ===
def upload_to_azure(local_file, blob_path, container):
    blob = BlobClient.from_connection_string(
        conn_str, container_name=container, blob_name=blob_path
    )
    with open(local_file, "rb") as f:
        blob.upload_blob(f, overwrite=True)
    print(f"✅ Uploaded: {local_file} → {container}/{blob_path}")

upload_to_azure(local_path, blob_path, container_name)
