#!/usr/bin/env python3
"""
IntertieLMP Gap Filler
Scrapes missing IntertieLMP files from IESO historical site and uploads to Azure
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
        filter_files_by_date, 
        get_latest_version_files,
        download_file
    )
    from azure_utils import (
        upload_to_blob, 
        build_blob_path, 
        check_blob_exists,
        get_latest_processed_date
    )
    from config import RAW_CONTAINER
except ImportError:
    print("❌ Error: Please copy config_template.py to config.py and add your Azure credentials")
    sys.exit(1)

# IESO URLs
HISTORICAL_INTERTIELMP_URL = "https://reports-public.ieso.ca/public/RealTimeIntertieLMP/"

def get_missing_dates() -> List[datetime]:
    """Determine which dates are missing from our cleaned data"""
    latest_date = get_latest_processed_date("cleaned-data", "IntertieLMP")
    
    if latest_date is None:
        print("❌ No existing data found in cleaned-data")
        return []
    
    print(f"📅 Latest processed date: {latest_date.strftime('%Y-%m-%d')}")
    
    # Calculate missing dates (up to yesterday)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    
    missing_dates = []
    current_date = latest_date + timedelta(days=1)
    
    while current_date <= yesterday:
        missing_dates.append(current_date)
        current_date += timedelta(days=1)
    
    return missing_dates

def scrape_intertielmp_gap() -> int:
    """Scrape missing IntertieLMP files and upload to Azure"""
    print("🚀 Starting IntertieLMP gap filling...")
    
    missing_dates = get_missing_dates()
    
    if not missing_dates:
        print("✅ No missing dates found - data is up to date!")
        return 0
    
    print(f"📋 Missing dates: {[d.strftime('%Y-%m-%d') for d in missing_dates]}")
    
    # Scrape IESO directory
    print(f"🌐 Scraping: {HISTORICAL_INTERTIELMP_URL}")
    all_files = scrape_ieso_directory(HISTORICAL_INTERTIELMP_URL, r'\.xml$')
    
    if not all_files:
        print("❌ No files found on IESO site")
        return 0
    
    print(f"📁 Found {len(all_files)} total XML files")
    
    # Filter files for missing dates
    target_files = []
    for missing_date in missing_dates:
        date_files = filter_files_by_date(all_files, missing_date, missing_date)
        target_files.extend(date_files)
    
    if not target_files:
        print("❌ No files found for missing dates")
        return 0
    
    # Get latest versions only
    target_files = get_latest_version_files(target_files)
    
    print(f"🎯 Target files ({len(target_files)}):")
    for file in target_files[:5]:  # Show first 5
        print(f"   • {file['name']}")
    if len(target_files) > 5:
        print(f"   ... and {len(target_files) - 5} more")
    
    # Download and upload files
    success_count = 0
    
    for file in target_files:
        try:
            blob_path = build_blob_path("IntertieLMP", file['name'])
            
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
        files_processed = scrape_intertielmp_gap()
        
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