from azure.storage.blob import BlobServiceClient, BlobClient
from io import BytesIO
import os
from datetime import datetime
from typing import List, Dict
try:
    from config import ACCOUNT_NAME, ACCOUNT_KEY, RAW_CONTAINER, CLEANED_CONTAINER
except ImportError:
    from config_template import ACCOUNT_NAME, ACCOUNT_KEY, RAW_CONTAINER, CLEANED_CONTAINER

def get_blob_service_client():
    """Get Azure Blob Service Client"""
    return BlobServiceClient(
        f"https://{ACCOUNT_NAME}.blob.core.windows.net", 
        credential=ACCOUNT_KEY
    )

def upload_to_blob(data: bytes, blob_path: str, container: str = RAW_CONTAINER) -> bool:
    """Upload data to Azure blob storage"""
    try:
        service_client = get_blob_service_client()
        container_client = service_client.get_container_client(container)
        container_client.upload_blob(name=blob_path, data=data, overwrite=True)
        print(f"✅ Uploaded: {blob_path} to {container}")
        return True
    except Exception as e:
        print(f"❌ Upload failed for {blob_path}: {e}")
        return False

def list_blobs_in_path(container: str, path_prefix: str) -> List[str]:
    """List all blobs in a specific path"""
    try:
        service_client = get_blob_service_client()
        container_client = service_client.get_container_client(container)
        
        blob_names = []
        for blob in container_client.list_blobs(name_starts_with=path_prefix):
            blob_names.append(blob.name)
        
        return blob_names
    except Exception as e:
        print(f"❌ Error listing blobs in {container}/{path_prefix}: {e}")
        return []

def get_latest_processed_date(container: str, dataset: str) -> datetime:
    """Get the latest date for which we have processed data"""
    try:
        blob_names = list_blobs_in_path(container, f"{dataset}/year=2025/")
        
        if not blob_names:
            return None
        
        latest_date = None
        
        for blob_name in blob_names:
            import re
            match = re.search(r'month=(\d{2})/day=(\d{2})', blob_name)
            if match:
                month, day = int(match.group(1)), int(match.group(2))
                file_date = datetime(2025, month, day)
                
                if latest_date is None or file_date > latest_date:
                    latest_date = file_date
        
        return latest_date
    except Exception as e:
        print(f"❌ Error getting latest date for {dataset}: {e}")
        return None

def build_blob_path(dataset: str, filename: str, file_date: datetime = None) -> str:
    """Build standardized blob path for a file"""
    if file_date is None:
        from scraper_utils import extract_date_from_filename
        file_date = extract_date_from_filename(filename)
    
    if file_date is None:
        file_date = datetime.now()
    
    # Build hierarchical path
    if dataset in ["EnergyLMP", "IntertieLMP"]:
        return f"{dataset}/year={file_date.year}/month={file_date.month:02d}/day={file_date.day:02d}/{filename}"
    else:
        return f"{dataset}/year={file_date.year}/{filename}"

def check_blob_exists(blob_path: str, container: str) -> bool:
    """Check if a blob already exists"""
    try:
        service_client = get_blob_service_client()
        blob_client = service_client.get_blob_client(container=container, blob=blob_path)
        blob_client.get_blob_properties()
        return True
    except Exception:
        return False 