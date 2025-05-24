import os
import pandas as pd
import xml.etree.ElementTree as ET
from azure.storage.blob import BlobServiceClient
from io import BytesIO
from datetime import datetime, timedelta
import re

# --- CONFIG ---
# Copy config_template.py to config.py and fill in your Azure credentials
try:
    from config import ACCOUNT_NAME, ACCOUNT_KEY, RAW_CONTAINER, CLEANED_CONTAINER
except ImportError:
    print("❌ config.py not found. Please copy config_template.py to config.py and fill in your Azure credentials.")
    exit(1)

PREFIX = "IntertieLMP/year=2025/"

# --- SETUP ---
service_client = BlobServiceClient(
    f"https://{ACCOUNT_NAME}.blob.core.windows.net", credential=ACCOUNT_KEY
)
raw = service_client.get_container_client(RAW_CONTAINER)
cleaned = service_client.get_container_client(CLEANED_CONTAINER)

def parse_intertie_name(intertie_name):
    """Parse intertie name like 'PQ.BEAUHARNOIS_PQBE:LMP' into components"""
    # Remove :LMP suffix if present
    name = intertie_name.replace(':LMP', '')
    
    # Split by dot to get location and connection_code
    if '.' in name:
        location, connection_code = name.split('.', 1)
        
        # Split connection_code by underscore to get connection and code
        if '_' in connection_code:
            connection, code = connection_code.split('_', 1)
        else:
            connection = connection_code
            code = ''
    else:
        location = ''
        connection = name
        code = ''
    
    return {
        'location': location,
        'connection': connection,
        'code': code
    }

def process_intertie_xml(xml_data):
    """Process IntertieLMP XML data and return cleaned DataFrame"""
    
    # Parse XML
    try:
        root = ET.fromstring(xml_data)
        namespace = {'ns': 'http://www.ieso.ca/schema'}
    except Exception as e:
        print(f"❌ XML parsing error: {e}")
        return None
    
    # Extract metadata
    delivery_date = root.find('.//ns:DeliveryDate', namespace)
    delivery_hour = root.find('.//ns:DeliveryHour', namespace)
    
    if delivery_date is None or delivery_hour is None:
        print("❌ Missing delivery date or hour in XML")
        return None
    
    base_date = delivery_date.text
    base_hour = int(delivery_hour.text)
    
    # Find all intertie prices
    intertie_prices = root.findall('.//ns:IntertieLMPrice', namespace)
    
    # Process all interties and intervals
    records = []
    
    for intertie in intertie_prices:
        intertie_name_elem = intertie.find('.//ns:IntertiePLName', namespace)
        intervals = intertie.findall('.//ns:IntervalLMP', namespace)
        
        if intertie_name_elem is None:
            continue
            
        intertie_name = intertie_name_elem.text
        name_parts = parse_intertie_name(intertie_name)
        
        # Process intervals (expecting 60 intervals = 5 sets of 12)
        interval_counter = 0
        
        for interval in intervals:
            interval_num = interval.find('ns:Interval', namespace)
            lmp = interval.find('ns:LMP', namespace)
            flag = interval.find('ns:Flag', namespace)
            
            if interval_num is not None and lmp is not None:
                interval_val = int(interval_num.text)
                lmp_val = float(lmp.text)
                flag_val = flag.text if flag is not None else ""
                
                # Calculate which set this interval belongs to (0-based)
                interval_set = interval_counter // 12
                
                # Calculate timestamp
                # Assume sets go backwards from delivery hour: hours 19,20,21,22,23 for sets 0,1,2,3,4
                hour_offset = -(4 - interval_set)  # -4,-3,-2,-1,0 hours before delivery hour
                target_hour = base_hour + hour_offset
                
                # Create base datetime for this hour
                base_datetime = datetime.strptime(f"{base_date} {target_hour:02d}:00:00", "%Y-%m-%d %H:%M:%S")
                timestamp = base_datetime + timedelta(minutes=(interval_val - 1) * 5)
                
                records.append({
                    'timestamp': timestamp,
                    'intertie_name': intertie_name,
                    'location': name_parts['location'],
                    'connection': name_parts['connection'], 
                    'code': name_parts['code'],
                    'interval_set': interval_set,
                    'interval': interval_val,
                    'lmp_value': lmp_val,
                    'flag': flag_val
                })
                
                interval_counter += 1
    
    if not records:
        print("❌ No valid records found in XML")
        return None
        
    # Create DataFrame
    df = pd.DataFrame(records)
    
    # Sort by timestamp and intertie_name for consistency
    df = df.sort_values(['timestamp', 'intertie_name']).reset_index(drop=True)
    
    return df

# --- PROCESS ALL XML FILES ---
processed_count = 0
error_count = 0

for blob in raw.list_blobs(name_starts_with=PREFIX):
    blob_name = blob.name
    print(f"📥 Processing: {blob_name}")

    # Skip non-XML files
    if not blob_name.endswith(".xml"):
        print(f"⏭️  Skipping non-XML file: {blob_name}")
        continue

    try:
        # Download XML data directly into memory
        xml_data = raw.get_blob_client(blob_name).download_blob().readall()
        
        # Process XML and get cleaned DataFrame
        df = process_intertie_xml(xml_data)
        
        if df is None or df.empty:
            print(f"❌ No data extracted from: {blob_name}")
            error_count += 1
            continue
        
        print(f"✅ Extracted {len(df)} records from {df['intertie_name'].nunique()} interties")
        print(f"   Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"   Non-zero LMPs: {(df['lmp_value'] != 0).sum()}/{len(df)} ({(df['lmp_value'] != 0).sum()/len(df)*100:.1f}%)")
        
        # Convert DataFrame to CSV in memory
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        # Create cleaned blob name (replace .xml with .csv)
        cleaned_blob_name = blob_name.replace('.xml', '.csv')
        
        # Upload directly to cleaned container
        print(f"⏫ Uploading cleaned data to: {cleaned_blob_name}")
        cleaned.upload_blob(name=cleaned_blob_name, data=csv_data, overwrite=True)
        
        processed_count += 1
        
    except Exception as e:
        print(f"❌ Error processing {blob_name}: {e}")
        error_count += 1
        continue

print(f"\n🎉 PROCESSING COMPLETE!")
print(f"✅ Successfully processed: {processed_count} files")
print(f"❌ Errors: {error_count} files")
print(f"📊 Cleaned IntertieLMP data uploaded to '{CLEANED_CONTAINER}' container")

if processed_count > 0:
    print(f"\n📋 CLEANED DATA STRUCTURE:")
    print("   Columns: timestamp, intertie_name, location, connection, code, interval_set, interval, lmp_value, flag")
    print("   • timestamp: Calculated from delivery date/hour + interval set + interval")
    print("   • intertie_name: Original full name (e.g., 'PQ.BEAUHARNOIS_PQBE:LMP')")
    print("   • location: Jurisdiction code (e.g., 'PQ', 'MB', 'NY')")
    print("   • connection: Connection point name (e.g., 'BEAUHARNOIS')")
    print("   • code: Connection code (e.g., 'PQBE')")
    print("   • interval_set: Hour grouping (0-4 for 5 hours)")
    print("   • interval: 5-minute interval within hour (1-12)")
    print("   • lmp_value: Locational Marginal Price (keeps zeros)")
    print("   • flag: Data quality flag (preserved, mostly 'DSO-RD')") 