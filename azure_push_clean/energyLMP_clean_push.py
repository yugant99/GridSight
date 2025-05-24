import os
import pandas as pd
from azure.storage.blob import BlobServiceClient
from io import BytesIO

# --- CONFIG ---
ACCOUNT_NAME = "YOUR_AZURE_STORAGE_ACCOUNT"
ACCOUNT_KEY = "YOUR_AZURE_STORAGE_KEY_HERE"
RAW_CONTAINER = "raw-data"
CLEANED_CONTAINER = "cleaned-data"
PREFIX = "EnergyLMP/year=2025/"
TEMP_DIR = "lmp_cleaned"

# --- SETUP ---
os.makedirs(TEMP_DIR, exist_ok=True)
service_client = BlobServiceClient(
    f"https://{ACCOUNT_NAME}.blob.core.windows.net", credential=ACCOUNT_KEY
)
raw = service_client.get_container_client(RAW_CONTAINER)
cleaned = service_client.get_container_client(CLEANED_CONTAINER)

def extract_date_from_blob(blob_name):
    # expect path like: EnergyLMP/year=2025/month=05/day=19/PUB_RealtimeEnergyLMP_2025051923_v12.csv
    import re
    match = re.search(r'LMP_(\d{8})(\d{2})', blob_name)
    if match:
        date_str = match.group(1)  # 20250519
        return pd.to_datetime(date_str)
    return None

# --- PROCESS ALL FILES ---
for blob in raw.list_blobs(name_starts_with=PREFIX):
    blob_name = blob.name
    print(f"📥 {blob_name}")

    # skip non-csv
    if not blob_name.endswith(".csv"):
        continue

    # download + read with skiprows=1
    data = raw.get_blob_client(blob_name).download_blob().readall()
    try:
        df = pd.read_csv(BytesIO(data), skiprows=1)
    except Exception as e:
        print(f"❌ Failed: {blob_name} — {e}")
        continue

    # clean columns
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # create timestamp column
    file_date = extract_date_from_blob(blob_name)
    if file_date is not None:
        df['timestamp'] = file_date + pd.to_timedelta((df['interval'] - 1) * 5, unit='min')
    else:
        print(f"⚠️ Date missing in filename: {blob_name}")
        continue

    df.dropna(inplace=True)

    # save locally
    cleaned_path = os.path.join(TEMP_DIR, os.path.basename(blob_name))
    df.to_csv(cleaned_path, index=False)

    # upload to cleaned container
    print(f"⏫ Uploading cleaned → {blob_name}")
    with open(cleaned_path, "rb") as f:
        cleaned.upload_blob(name=blob_name, data=f, overwrite=True)

print("\n✅ All LMP files cleaned and uploaded.")
