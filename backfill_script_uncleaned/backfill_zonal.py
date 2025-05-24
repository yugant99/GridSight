import requests
import re
from datetime import datetime, timedelta, timezone
from azure.storage.blob import BlobServiceClient
from bs4 import BeautifulSoup

# --- CONFIG ---

ACCOUNT_NAME = "YOUR_AZURE_STORAGE_ACCOUNT"
ACCOUNT_KEY = "YOUR_AZURE_STORAGE_KEY_HERE"
CONTAINER_NAME = "raw-data"
BASE_URL = "https://reports-public.ieso.ca/public/DemandZonal/"
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

def get_file_links():
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    return [a["href"] for a in soup.find_all("a", href=True) if "PUB_DemandZonal" in a["href"]]

def extract_year_version(filename):
    match = re.search(r'DemandZonal_(\d{4})(?:_v(\d+))?', filename)
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
        # Ensure version is treated as a number for comparison, defaulting to 0 if not present
        current_version = version if version is not None else 0
        if year not in latest or current_version > latest[year][1]:
            latest[year] = (f, current_version)
    return [item[0] for item in latest.values()]

def is_recent_file_zonal(filename, cutoff_date_obj):
    year, _ = extract_year_version(filename)
    if year:
        if year not in [2024, 2025]:
            return False
        file_represents_period_until = datetime(year, 12, 31, tzinfo=timezone.utc)
        return file_represents_period_until >= cutoff_date_obj
    return False

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

print(f"📦 Starting backfill for Zonal Demand (cutoff: {CUTOFF_DATE.strftime('%Y-%m-%d')})")

files = get_file_links()
latest_files = get_latest_versions(files)

for file_name in latest_files:
    year, _ = extract_year_version(file_name)
    # year variable is already extracted, use it directly for logging if needed

    if not is_recent_file_zonal(file_name, CUTOFF_DATE):
        print(f"⏩ Skipped (not recent or outside 2024/2025): {file_name}")
        continue

    full_url = BASE_URL + file_name
    # Ensure year for blob_path is correctly extracted if needed again, or passed
    # extract_year_version already gives us the year
    blob_path = f"DemandZonal/year={year}/{file_name}"

    print(f"⬇️ Downloading {file_name}")
    download_file(full_url, LOCAL_TEMP_FILE)
    upload_to_blob(LOCAL_TEMP_FILE, blob_path)

print("\n🎉 Zonal Demand backfill complete.")
