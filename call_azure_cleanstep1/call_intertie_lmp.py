from azure.storage.blob import BlobClient
import os

# === config ===
conn_str = "DefaultEndpointsProtocol=https;AccountName=YOUR_AZURE_STORAGE_ACCOUNT;AccountKey=YOUR_AZURE_STORAGE_KEY_HERE;EndpointSuffix=core.windows.net"
container_name = "raw-data"
blob_name = "IntertieLMP/year=2025/month=05/day=01/PUB_RealTimeIntertieLMP_2025050123_v12.xml"
local_dir = "Azure_backfill"
local_file_path = os.path.join(local_dir, "PUB_RealTimeIntertieLMP_2025050123_v12.xml")

# ensure dir
os.makedirs(local_dir, exist_ok=True)

# download blob
blob = BlobClient.from_connection_string(conn_str, container_name, blob_name)
with open(local_file_path, "wb") as f:
    f.write(blob.download_blob().readall())

print(f"✅ downloaded to {local_file_path}") 