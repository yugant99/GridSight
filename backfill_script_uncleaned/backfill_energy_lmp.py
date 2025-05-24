import requests
import re
from datetime import datetime, timezone
from azure.storage.blob import BlobServiceClient
from bs4 import BeautifulSoup
import os

# --- CONFIG ---
ACCOUNT_NAME = "YOUR_AZURE_STORAGE_ACCOUNT"
ACCOUNT_KEY = "YOUR_AZURE_STORAGE_KEY_HERE"
CONTAINER_NAME = "raw-data"
BASE_URL = "https://reports-public.ieso.ca/public/RealtimeEnergyLMP/"
LOCAL_TEMP_FILE = "temp_download.csv"
CUTOFF_TIMESTAMP = datetime(2025, 5, 20, 0, 0, 0, tzinfo=timezone.utc)  # include May 19 24:00

# --- INIT AZURE BLOB ---
blob_service_client = BlobServiceClient(
    account_url=f"https://{ACCOUNT_NAME}.blob.core.windows.net",
    credential=ACCOUNT_KEY
)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# --- UTILS ---

def get_file_links():
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    return [a["href"] for a in soup.find_all("a", href=True) if re.search(r'LMP_\d{10}(_v\d+)?\.csv', a["href"])]

def extract_datetime_version(filename):
    match = re.search(r'LMP_(\d{10})(?:_v(\d+))?', filename)
    if match:
        date_str = match.group(1)
        version = int(match.group(2)) if match.group(2) else 0
        try:
            dt = datetime.strptime(date_str, "%Y%m%d%H").replace(tzinfo=timezone.utc)
            return dt, version
        except:
            return None, None
    return None, None

def get_latest_daily_files(file_list):
    """Get the latest/most complete file for each day (highest hour + version)"""
    daily_files = {}
    
    for f in file_list:
        dt, version = extract_datetime_version(f)
        if dt is None or dt > CUTOFF_TIMESTAMP:
            continue
            
        # Group by date only (YYYYMMDD)
        date_key = dt.strftime("%Y%m%d")
        hour = dt.hour
        
        # Store the file if it's the latest hour for this date, or same hour but higher version
        if date_key not in daily_files:
            daily_files[date_key] = (f, hour, version, dt)
        else:
            existing_file, existing_hour, existing_version, existing_dt = daily_files[date_key]
            
            # Prefer files with higher hour (later in the day), or same hour with higher version
            if hour > existing_hour or (hour == existing_hour and version > existing_version):
                daily_files[date_key] = (f, hour, version, dt)
    
    # Return just the filenames, sorted by date
    result = []
    for date_key in sorted(daily_files.keys()):
        filename, hour, version, dt = daily_files[date_key]
        result.append((filename, dt))
    
    return result

def blob_exists(blob_name):
    return container_client.get_blob_client(blob_name).exists()

def download_file(url, path):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

def upload_to_blob(local_path, blob_path):
    if blob_exists(blob_path):
        print(f"⚠️  Skipping upload — already exists: {blob_path}")
        return
    with open(local_path, "rb") as data:
        container_client.upload_blob(name=blob_path, data=data, overwrite=True)
        print(f"✅ Uploaded: {blob_path}")

# --- MAIN ---

print(f"📦 Starting Energy LMP backfill - Latest daily files (Jan 1 → {CUTOFF_TIMESTAMP.strftime('%Y-%m-%d')})")

files = get_file_links()
daily_files = get_latest_daily_files(files)
print(f"🔍 Total daily files selected: {len(daily_files)} (one per day)\n")

for file_name, dt in daily_files:
    year = dt.year
    month = f"{dt.month:02}"
    day = f"{dt.day:02}"
    hour = f"{dt.hour:02}"
    blob_path = f"EnergyLMP/year={year}/month={month}/day={day}/{file_name}"

    print(f"⬇️ Downloading {file_name} (Date: {dt.strftime('%Y-%m-%d')}, Hour: {hour}:00)")
    download_file(BASE_URL + file_name, LOCAL_TEMP_FILE)
    upload_to_blob(LOCAL_TEMP_FILE, blob_path)

# Clean up temp file
if os.path.exists(LOCAL_TEMP_FILE):
    os.remove(LOCAL_TEMP_FILE)

print("\n🎉 Energy LMP backfill complete - One file per day uploaded.")
