import pandas as pd
from azure.storage.blob import BlobServiceClient
from io import BytesIO

# --- CONFIG ---
ACCOUNT_NAME = "YOUR_AZURE_STORAGE_ACCOUNT"
ACCOUNT_KEY = "YOUR_AZURE_STORAGE_KEY_HERE"
CONTAINER = "raw-data"
BLOB_PATH = "EnergyLMP/year=2025/month=05/day=19/PUB_RealtimeEnergyLMP_2025051923_v12.csv"  # <--- choose any one here

# --- AZURE SETUP ---
service_client = BlobServiceClient(
    account_url=f"https://{ACCOUNT_NAME}.blob.core.windows.net",
    credential=ACCOUNT_KEY
)
blob_client = service_client.get_container_client(CONTAINER).get_blob_client(BLOB_PATH)

# --- DOWNLOAD & INSPECT ---
print(f"📥 Downloading {BLOB_PATH}...")
blob_data = blob_client.download_blob().readall()

# decode first few lines for manual inspection
text = blob_data.decode("utf-8").splitlines()

print("\n🧾 First 10 lines of file:")
for i, line in enumerate(text[:10]):
    print(f"{i}: {line}")

# auto-detect header line (e.g., the line starting with "Delivery Hour")
header_index = next((i for i, line in enumerate(text) if line.lower().startswith("delivery hour")), None)

print(f"\n📌 Detected header at line: {header_index}")
print("🔍 Attempting to read CSV with skiprows...")

# read using detected header
df = pd.read_csv(BytesIO(blob_data), skiprows=header_index)
print("\n✅ Sample data:")
print(df.head())

print("\n🧠 Column names:")
print(df.columns.tolist())
