import os
from azure.storage.blob import BlobClient

# 🔐 secure credentials
conn_str = "DefaultEndpointsProtocol=https;AccountName=YOUR_AZURE_STORAGE_ACCOUNT;AccountKey=YOUR_AZURE_STORAGE_KEY_HERE;EndpointSuffix=core.windows.net"  # or use account name + key

# 💾 define blob details
container_name = "raw-data"
blob_name = "Demand/year=2025/PUB_Demand_2025.csv"
local_dir = "Azure_backfill"
local_file_path = os.path.join(local_dir, "PUB_Demand.csv")

# 📁 ensure local dir exists
os.makedirs(local_dir, exist_ok=True)

# 📥 connect to blob and download
blob = BlobClient.from_connection_string(conn_str, container_name, blob_name)

with open(local_file_path, "wb") as file:
    file.write(blob.download_blob().readall())

print(f"✅ Downloaded '{blob_name}' to '{local_file_path}'")
