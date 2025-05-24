import pandas as pd
from azure.storage.blob import BlobServiceClient
from io import BytesIO

# Config
ACCOUNT_NAME = "YOUR_AZURE_STORAGE_ACCOUNT"
ACCOUNT_KEY = "YOUR_AZURE_STORAGE_KEY_HERE"
CLEANED_CONTAINER = "cleaned-data"

# Setup
service_client = BlobServiceClient(
    f"https://{ACCOUNT_NAME}.blob.core.windows.net", credential=ACCOUNT_KEY
)
cleaned = service_client.get_container_client(CLEANED_CONTAINER)

# Download one cleaned file to verify structure
blob_name = "IntertieLMP/year=2025/month=05/day=01/PUB_RealTimeIntertieLMP_2025050123_v12.csv"

print(f"📥 Downloading: {blob_name}")
csv_data = cleaned.get_blob_client(blob_name).download_blob().readall()
df = pd.read_csv(BytesIO(csv_data))

print(f"\n📊 CLEANED DATA VERIFICATION:")
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

print(f"\n📋 DATA SAMPLE:")
print(df.head(10))

print(f"\n🔍 DATA ANALYSIS:")
print(f"Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")
print(f"Unique interties: {df['intertie_name'].nunique()}")
print(f"Unique locations: {df['location'].unique()}")
print(f"Interval sets: {sorted(df['interval_set'].unique())}")
print(f"Intervals per set: {sorted(df['interval'].unique())}")

print(f"\n💰 LMP ANALYSIS:")
print(f"Non-zero LMPs: {(df['lmp_value'] != 0).sum()}/{len(df)} ({(df['lmp_value'] != 0).sum()/len(df)*100:.1f}%)")
print(f"LMP range: {df['lmp_value'].min():.2f} to {df['lmp_value'].max():.2f}")

print(f"\n🚩 FLAG ANALYSIS:")
print(df['flag'].value_counts())

print(f"\n✅ Verification complete!") 