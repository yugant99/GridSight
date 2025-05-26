#!/usr/bin/env python3
"""
Demand Gap Filler
Scrapes missing Demand files from IESO historical site and uploads to Azure
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from scraper_utils import (
        scrape_ieso_directory, 
        get_latest_version_files,
        download_file
    )
    from azure_utils import (
        upload_to_blob, 
        build_blob_path, 
        check_blob_exists,
        list_blobs_in_path
    )
    from config import RAW_CONTAINER
except ImportError:
    print("❌ Error: Please copy config_template.py to config.py and add your Azure credentials")
    sys.exit(1)

# IESO URLs
HISTORICAL_DEMAND_URL = "https://reports-public.ieso.ca/public/Demand/"

def get_latest_demand_version() -> str:
    """Get the latest Demand version we have in Azure"""
    try:
        blob_names = list_blobs_in_path(RAW_CONTAINER, "Demand/year=2025/")
        
        if not blob_names:
            return None
        
        latest_version = 0
        
        for blob_name in blob_names:
            # Extract version from filename
            import re
            match = re.search(r'_v(\d+)\.csv$', blob_name)
            if match:
                version = int(match.group(1))
                if version > latest_version:
                    latest_version = version
        
        return f"v{latest_version}" if latest_version > 0 else None
        
    except Exception as e:
        print(f"❌ Error getting latest Demand version: {e}")
        return None

def scrape_demand_gap() -> int:
    """Scrape missing Demand files and upload to Azure"""
    print("🚀 Starting Demand gap filling...")
    
    # Get latest version we have
    current_version = get_latest_demand_version()
    
    if current_version:
        print(f"📅 Latest version in Azure: {current_version}")
    else:
        print("📅 No existing Demand data found in Azure")
    
    # Scrape IESO directory
    print(f"🌐 Scraping: {HISTORICAL_DEMAND_URL}")
    all_files = scrape_ieso_directory(HISTORICAL_DEMAND_URL, r'2025.*\.csv$')
    
    if not all_files:
        print("❌ No files found on IESO site")
        return 0
    
    print(f"📁 Found {len(all_files)} total 2025 CSV files")
    
    # Get latest versions only
    target_files = get_latest_version_files(all_files)
    
    # Filter to only newer versions than what we have
    if current_version:
        current_version_num = int(current_version.replace('v', ''))
        filtered_files = []
        
        for file in target_files:
            import re
            match = re.search(r'_v(\d+)\.csv$', file['name'])
            if match:
                file_version = int(match.group(1))
                if file_version > current_version_num:
                    filtered_files.append(file)
            else:
                # Files without version numbers
                filtered_files.append(file)
        
        target_files = filtered_files
    
    if not target_files:
        print("✅ No newer Demand files found - data is up to date!")
        return 0
    
    print(f"🎯 Target files ({len(target_files)}):")
    for file in target_files:
        print(f"   • {file['name']}")
    
    # Download and upload files
    success_count = 0
    
    for file in target_files:
        try:
            blob_path = build_blob_path("Demand", file['name'])
            
            if check_blob_exists(blob_path, RAW_CONTAINER):
                print(f"⏭️  Already exists: {file['name']}")
                success_count += 1
                continue
            
            print(f"📥 Downloading: {file['name']}")
            file_data = download_file(file['url'])
            
            if upload_to_blob(file_data, blob_path, RAW_CONTAINER):
                success_count += 1
            else:
                print(f"❌ Upload failed: {file['name']}")
                
        except Exception as e:
            print(f"❌ Error processing {file['name']}: {e}")
            continue
    
    print(f"\n🎉 Gap filling complete!")
    print(f"✅ Successfully processed: {success_count}/{len(target_files)} files")
    
    return success_count

def main():
    """Main entry point"""
    try:
        files_processed = scrape_demand_gap()
        
        if files_processed > 0:
            print(f"\n📋 NEXT STEPS:")
            print(f"1. Run the cleaning script to process these raw files")
            print(f"2. Verify Synapse external tables see the new data")
            print(f"3. Set up daily automation for ongoing updates")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 