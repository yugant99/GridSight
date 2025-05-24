import requests
import re
from datetime import datetime, timedelta, timezone
from azure.storage.blob import BlobServiceClient
from bs4 import BeautifulSoup

# --- CONFIG ---

ACCOUNT_NAME = "YOUR_AZURE_STORAGE_ACCOUNT"
ACCOUNT_KEY = "YOUR_AZURE_STORAGE_KEY_HERE"
CONTAINER_NAME = "raw-data"
BASE_URL = "https://reports-public.ieso.ca/public/GenOutputbyFuelHourly/"
LOCAL_TEMP_FILE = "temp_download.xml"

# --- DATE SETUP ---

TODAY = datetime.now(timezone.utc)

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
    return [a["href"] for a in soup.find_all("a", href=True) if "PUB_GenOutputbyFuelHourly_" in a["href"]]

def extract_year_version(filename):
    match = re.search(r'FuelHourly_(\d{4})(?:_v(\d+))?', filename)
    if match:
        year = int(match.group(1))
        version = int(match.group(2)) if match.group(2) else 0
        return year, version
    return None, None

def get_latest_versions(file_list):
    latest = {}
    for f in file_list:
        year, version = extract_year_version(f)
        if year is None:
            continue
        if year not in latest or version > latest[year][1]:
            latest[year] = (f, version)
    return [item[0] for item in latest.values()]

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

print("📦 Starting backfill for GenMix (Generator Output by Fuel Hourly)")

files = get_file_links()
latest_files = get_latest_versions(files)

for file_name in latest_files:
    year, _ = extract_year_version(file_name)
    if year < TODAY.year - 1:  # only fetch 2024, 2025
        print(f"⏩ Skipped (too old): {file_name}")
        continue

    full_url = BASE_URL + file_name
    blob_path = f"GenMix/year={year}/{file_name}"

    print(f"⬇️ Downloading {file_name}")
    download_file(full_url, LOCAL_TEMP_FILE)
    upload_to_blob(LOCAL_TEMP_FILE, blob_path)

print("\n🎉 GenMix backfill complete.")
