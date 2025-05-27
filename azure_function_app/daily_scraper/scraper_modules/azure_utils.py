import os
from azure.storage.blob import BlobServiceClient
from datetime import datetime
import logging
from typing import List, Optional

# Get credentials from environment variables (Azure Functions)
ACCOUNT_NAME = os.environ.get('AZURE_STORAGE_ACCOUNT', 'datastoreyugant')
ACCOUNT_KEY = os.environ.get('AZURE_STORAGE_KEY')

if not ACCOUNT_KEY:
    raise ValueError("AZURE_STORAGE_KEY environment variable not set")

RAW_CONTAINER = "raw-data"
CLEANED_CONTAINER = "cleaned-data"

# Create blob service client
blob_service_client = BlobServiceClient(
    account_url=f"https://{ACCOUNT_NAME}.blob.core.windows.net",
    credential=ACCOUNT_KEY
)

def upload_to_blob(file_data: bytes, blob_path: str, container_name: str) -> bool:
    """Upload file data to Azure blob storage"""
    try:
        blob_client = blob_service_client.get_blob_client(
            container=container_name, 
            blob=blob_path
        )
        blob_client.upload_blob(file_data, overwrite=True)
        logging.info(f"✅ Uploaded: {blob_path}")
        return True
    except Exception as e:
        logging.error(f"❌ Upload failed for {blob_path}: {e}")
        return False

def build_blob_path(dataset_name: str, filename: str) -> str:
    """Build hierarchical blob path from filename"""
    import re
    
    # Extract date from filename
    date_match = re.search(r'(\d{4})(\d{2})(\d{2})', filename)
    if date_match:
        year, month, day = date_match.groups()
        return f"{dataset_name}/year={year}/month={month}/day={day}/{filename}"
    else:
        # For annual files without specific dates
        year = datetime.now().year
        return f"{dataset_name}/year={year}/{filename}"

def check_blob_exists(blob_path: str, container_name: str) -> bool:
    """Check if blob exists in container"""
    try:
        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=blob_path
        )
        blob_client.get_blob_properties()
        return True
    except:
        return False

def list_blobs_in_path(container_name: str, path_prefix: str) -> List[str]:
    """List all blobs with given path prefix"""
    try:
        container_client = blob_service_client.get_container_client(container_name)
        blob_list = container_client.list_blobs(name_starts_with=path_prefix)
        return [blob.name for blob in blob_list]
    except Exception as e:
        logging.error(f"❌ Error listing blobs: {e}")
        return []

def get_latest_processed_date(container_name: str, dataset_name: str) -> Optional[datetime]:
    """Get the latest date for which we have processed data"""
    try:
        blobs = list_blobs_in_path(container_name, f"{dataset_name}/")
        if not blobs:
            return None
        
        dates = []
        for blob in blobs:
            import re
            date_match = re.search(r'day=(\d{2})', blob)
            if date_match:
                day = int(date_match.group(1))
                month_match = re.search(r'month=(\d{2})', blob)
                year_match = re.search(r'year=(\d{4})', blob)
                if month_match and year_match:
                    month = int(month_match.group(1))
                    year = int(year_match.group(1))
                    dates.append(datetime(year, month, day))
        
        return max(dates) if dates else None
    except Exception as e:
        logging.error(f"❌ Error getting latest date: {e}")
        return None
