import requests
import re
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient
from bs4 import BeautifulSoup
from datetime import timezone


# --- CONFIG ---

ACCOUNT_NAME = "YOUR_AZURE_STORAGE_ACCOUNT"
ACCOUNT_KEY = "YOUR_AZURE_STORAGE_KEY_HERE"
CONTAINER_NAME = "raw-data"
BASE_URL = "https://reports-public.ieso.ca/public/Demand/"
LOCAL_TEMP_FILE = "temp_download.csv"

# --- DATE SETUP ---

TODAY = datetime.now(timezone.utc)
# Calculate the first day of the month three months ago
MONTH_OFFSET = 3
current_month = TODAY.month
current_year = TODAY.year

cutoff_month = current_month - MONTH_OFFSET
cutoff_year = current_year
if cutoff_month <= 0:
    cutoff_month += 12
    cutoff_year -= 1

CUTOFF_DATE = datetime(cutoff_year, cutoff_month, 1, tzinfo=timezone.utc)


# --- INIT AZURE BLOB ---

blob_service_client = BlobServiceClient(
    account_url=f"https://{ACCOUNT_NAME}.blob.core.windows.net",
    credential=ACCOUNT_KEY
)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# --- UTILS ---

def is_recent_file(filename):
    match = re.search(r'Demand_(\d{4})', filename)  # matches e.g. PUB_Demand_2025.csv
    if match:
        year = int(match.group(1))

        if year not in [2024, 2025]:
            return False

        # Consider the file relevant for the entire year it represents.
        # We want to include it if any part of that year falls after the CUTOFF_DATE.
        # More simply, if the end of the file's year is after or on the CUTOFF_DATE.
        file_represents_period_until = datetime(year, 12, 31, tzinfo=timezone.utc) # End of the year for the file

        return file_represents_period_until >= CUTOFF_DATE

    return False

def get_file_links():
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    return [a["href"] for a in soup.find_all("a", href=True) if "PUB_Demand_" in a["href"]]

print("📁 Files found:")
for file in get_file_links():
    print(" -", file)

def download_file(url, path):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

def upload_to_blob(local_path, blob_path):
    with open(local_path, "rb") as data:
        container_client.upload_blob(name=blob_path, data=data, overwrite=True)
        print(f"✅ Uploaded: {blob_path}")

# --- MAIN ---

print(f"📦 Starting backfill for Demand data (cutoff: {CUTOFF_DATE.strftime('%Y-%m-%d')})")

for file_name in get_file_links():
    if not is_recent_file(file_name):
        print(f"⏩ Skipped (not recent): {file_name}")
        continue
    print(f"Accepted: {file_name}")    
    full_url = BASE_URL + file_name
    year_match = re.search(r'(\d{4})', file_name)
    year = year_match.group(1) if year_match else "unknown"
    blob_path = f"Demand/year={year}/{file_name}"

    print(f"⬇️ Downloading {file_name}")
    download_file(full_url, LOCAL_TEMP_FILE)
    upload_to_blob(LOCAL_TEMP_FILE, blob_path)

print("\n🎉 Demand backfill complete.")
