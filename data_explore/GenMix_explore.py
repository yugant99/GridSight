import xml.etree.ElementTree as ET
import pandas as pd
import os

# === local GenMix file ===
xml_path = "/Users/yuganthareshsoni/project_tester_1/call_azure_cleanstep1/Azure_backfill/PUB_GenOutputbyFuelHourly_2025_v139.xml"

# === parse XML ===
tree = ET.parse(xml_path)
root = tree.getroot()

# === inspect the XML structure and extract data ===
rows = []

# Navigate through the correct XML structure
for daily_data in root.findall(".//{http://www.ieso.ca/schema}DailyData"):
    day_elem = daily_data.find(".//{http://www.ieso.ca/schema}Day")
    day = day_elem.text if day_elem is not None else None
    
    for hourly_data in daily_data.findall(".//{http://www.ieso.ca/schema}HourlyData"):
        hour_elem = hourly_data.find(".//{http://www.ieso.ca/schema}Hour")
        hour = hour_elem.text if hour_elem is not None else None
        
        for fuel_total in hourly_data.findall(".//{http://www.ieso.ca/schema}FuelTotal"):
            fuel_elem = fuel_total.find(".//{http://www.ieso.ca/schema}Fuel")
            fuel = fuel_elem.text if fuel_elem is not None else None
            
            energy_value = fuel_total.find(".//{http://www.ieso.ca/schema}EnergyValue")
            if energy_value is not None:
                output_quality_elem = energy_value.find(".//{http://www.ieso.ca/schema}OutputQuality")
                output_elem = energy_value.find(".//{http://www.ieso.ca/schema}Output")
                
                output_quality = output_quality_elem.text if output_quality_elem is not None else None
                output = output_elem.text if output_elem is not None else None
                
                row = {
                    'day': day,
                    'hour': hour,
                    'fuel': fuel,
                    'output_quality': output_quality,
                    'output': output
                }
    rows.append(row)

print(f"✅ Total records found: {len(rows)}")

# === show first few records ===
for i, row in enumerate(rows[:5]):
        print(f"{i+1}: {row}")

# === convert to DataFrame ===
df = pd.DataFrame(rows)
print("\n🧠 Columns:", df.columns.tolist())
print("\n📊 Sample:")
print(df.head())

print(f"\n📈 Data Summary:")
print(f"- Date range: {df['day'].min()} to {df['day'].max()}")
print(f"- Fuel types: {df['fuel'].unique()}")
print(f"- Hour range: {df['hour'].min()} to {df['hour'].max()}")

# === CLEAN THE DATA ===
print("\n🧹 Cleaning data...")

# ensure correct types
df['day'] = pd.to_datetime(df['day'])
df['hour'] = df['hour'].astype(int)
df['output'] = df['output'].astype(float)

# create timestamp column
df['timestamp'] = df['day'] + pd.to_timedelta(df['hour'] - 1, unit='h')

# final clean - select only relevant columns and sort
df_clean = df[['timestamp', 'fuel', 'output']].sort_values('timestamp')

print(f"✅ Cleaned data shape: {df_clean.shape}")
print("\n📊 Cleaned sample:")
print(df_clean.head())

# === SAVE TO SPECIFIED DIRECTORY ===
output_dir = "/Users/yuganthareshsoni/project_tester_1/call_azure_cleanstep1/Azure_clean_notpushed"
os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(output_dir, "PUB_GenOutputbyFuelHourly_2025_v139_cleaned.csv")
df_clean.to_csv(output_file, index=False)

print(f"\n💾 Cleaned data saved to: {output_file}")
print(f"📊 Final data summary:")
print(f"- Records: {len(df_clean):,}")
print(f"- Date range: {df_clean['timestamp'].min()} to {df_clean['timestamp'].max()}")
print(f"- Fuel types: {sorted(df_clean['fuel'].unique())}")
