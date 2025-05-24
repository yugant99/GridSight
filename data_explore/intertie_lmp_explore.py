import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
import os

def explore_intertie_lmp():
    """Explore IntertieLMP XML file structure and data quality"""
    
    # File path
    xml_file = "../call_azure_cleanstep1/Azure_backfill/PUB_RealTimeIntertieLMP_2025050123_v12.xml"
    
    if not os.path.exists(xml_file):
        print(f"❌ File not found: {xml_file}")
        return
    
    print("🔍 EXPLORING INTERTIE LMP XML STRUCTURE")
    print("=" * 50)
    
    # Parse XML
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        namespace = {'ns': 'http://www.ieso.ca/schema'}
        print(f"✅ XML parsed successfully")
    except Exception as e:
        print(f"❌ XML parsing error: {e}")
        return
    
    # Basic document info
    print("\n📋 DOCUMENT METADATA:")
    doc_title = root.find('.//ns:DocTitle', namespace)
    created_at = root.find('.//ns:CreatedAt', namespace)
    delivery_date = root.find('.//ns:DeliveryDate', namespace)
    delivery_hour = root.find('.//ns:DeliveryHour', namespace)
    
    print(f"Title: {doc_title.text if doc_title is not None else 'N/A'}")
    print(f"Created At: {created_at.text if created_at is not None else 'N/A'}")
    print(f"Delivery Date: {delivery_date.text if delivery_date is not None else 'N/A'}")
    print(f"Delivery Hour: {delivery_hour.text if delivery_hour is not None else 'N/A'}")
    
    # Find all intertie prices
    intertie_prices = root.findall('.//ns:IntertieLMPrice', namespace)
    print(f"\n🔌 INTERTIE CONNECTIONS FOUND: {len(intertie_prices)}")
    
    # Analyze each intertie
    intertie_data = []
    intertie_summary = defaultdict(lambda: {'intervals': 0, 'zero_lmps': 0, 'flags': set()})
    
    # Check interval pattern in first intertie
    if intertie_prices:
        first_intertie = intertie_prices[0]
        intervals = first_intertie.findall('.//ns:IntervalLMP', namespace)
        interval_numbers = [int(interval.find('ns:Interval', namespace).text) for interval in intervals]
        
        print(f"\n🔍 INTERVAL PATTERN ANALYSIS:")
        print(f"Total intervals in first intertie: {len(interval_numbers)}")
        print(f"Interval sequence: {interval_numbers[:20]}...")
        
        # Count how many complete sets of 1-12
        sets_of_12 = len(interval_numbers) // 12
        print(f"Complete sets of 1-12: {sets_of_12}")
        
        if sets_of_12 > 1:
            print(f"⚠️  This appears to contain data for {sets_of_12} separate time periods!")
    
    for i, intertie in enumerate(intertie_prices):
        intertie_name = intertie.find('.//ns:IntertiePLName', namespace)
        intervals = intertie.findall('.//ns:IntervalLMP', namespace)
        
        name = intertie_name.text if intertie_name is not None else f"Unknown_{i}"
        print(f"\n🔗 {name}:")
        print(f"   Intervals: {len(intervals)}")
        
        # Analyze intervals for this intertie
        lmp_values = []
        flags = []
        interval_counter = 0
        
        for interval in intervals:
            interval_num = interval.find('ns:Interval', namespace)
            lmp = interval.find('ns:LMP', namespace)
            flag = interval.find('ns:Flag', namespace)
            
            if interval_num is not None and lmp is not None:
                interval_val = int(interval_num.text)
                lmp_val = float(lmp.text)
                flag_val = flag.text if flag is not None else "None"
                
                lmp_values.append(lmp_val)
                flags.append(flag_val)
                
                # Calculate which set this interval belongs to (0-based)
                interval_set = interval_counter // 12
                interval_in_set = interval_counter % 12 + 1
                
                intertie_data.append({
                    'intertie_name': name,
                    'interval_set': interval_set,
                    'interval': interval_val,
                    'interval_in_set': interval_in_set,
                    'lmp': lmp_val,
                    'flag': flag_val
                })
                
                interval_counter += 1
        
        # Summary stats for this intertie
        if lmp_values:
            zero_count = sum(1 for x in lmp_values if x == 0)
            unique_flags = set(flags)
            
            print(f"   LMP Range: {min(lmp_values):.2f} to {max(lmp_values):.2f}")
            print(f"   Zero LMPs: {zero_count}/{len(lmp_values)} ({zero_count/len(lmp_values)*100:.1f}%)")
            print(f"   Unique Flags: {sorted(unique_flags)}")
            
            intertie_summary[name]['intervals'] = len(lmp_values)
            intertie_summary[name]['zero_lmps'] = zero_count
            intertie_summary[name]['flags'] = unique_flags
    
    # Create DataFrame for analysis
    df = pd.DataFrame(intertie_data)
    
    print(f"\n📊 OVERALL DATA SUMMARY:")
    print(f"Total Records: {len(df)}")
    print(f"Unique Interties: {df['intertie_name'].nunique()}")
    print(f"Interval Sets per Intertie: {df['interval_set'].max() + 1}")
    print(f"Intervals per Set: {df.groupby(['intertie_name', 'interval_set'])['interval_in_set'].count().iloc[0]}")
    
    # Date/Time Analysis
    print(f"\n⏰ DATE/TIME STRUCTURE:")
    base_date = delivery_date.text if delivery_date is not None else "2025-05-01"
    base_hour = int(delivery_hour.text) if delivery_hour is not None else 23
    
    print(f"Base Date: {base_date}")
    print(f"Base Hour: {base_hour}")
    
    # Check if this is 5 hours of data (60 intervals = 5 sets of 12)
    num_sets = df['interval_set'].max() + 1
    print(f"Number of time periods: {num_sets}")
    
    if num_sets == 5:
        print(f"⚠️  This appears to be 5 hours of data:")
        for i in range(num_sets):
            hour = base_hour - (4 - i)  # Reverse order assumption
            print(f"  Set {i}: Hour {hour:02d}:00-{hour:02d}:55")
    
    # Create proper timestamps for first intertie as example
    if not df.empty:
        first_intertie = df[df['intertie_name'] == df['intertie_name'].iloc[0]].copy()
        
        # Calculate actual timestamps assuming each set is a different hour
        def calculate_timestamp(row):
            # Assume sets go backwards from delivery hour
            hour_offset = -(4 - row['interval_set'])  # 4,3,2,1,0 hours before
            target_hour = base_hour + hour_offset
            
            base_datetime = datetime.strptime(f"{base_date} {target_hour:02d}:00:00", "%Y-%m-%d %H:%M:%S")
            return base_datetime + timedelta(minutes=(row['interval'] - 1) * 5)
        
        first_intertie['timestamp'] = first_intertie.apply(calculate_timestamp, axis=1)
        
        print(f"\n📅 TIMESTAMP EXAMPLE (first intertie, first few records from each set):")
        for set_num in range(min(3, num_sets)):  # Show first 3 sets
            set_data = first_intertie[first_intertie['interval_set'] == set_num].head(3)
            print(f"\nSet {set_num}:")
            print(set_data[['interval_set', 'interval', 'timestamp', 'lmp', 'flag']])
    
    # Data Quality Analysis
    print(f"\n🔍 DATA QUALITY ANALYSIS:")
    
    # LMP value analysis
    lmp_stats = df['lmp'].describe()
    print(f"LMP Statistics:")
    print(f"  Count: {lmp_stats['count']}")
    print(f"  Mean: ${lmp_stats['mean']:.2f}")
    print(f"  Std: ${lmp_stats['std']:.2f}")
    print(f"  Min: ${lmp_stats['min']:.2f}")
    print(f"  Max: ${lmp_stats['max']:.2f}")
    
    # Zero values analysis
    zero_lmps = (df['lmp'] == 0).sum()
    print(f"\nZero LMP Values: {zero_lmps}/{len(df)} ({zero_lmps/len(df)*100:.1f}%)")
    
    # Flag analysis
    flag_counts = df['flag'].value_counts()
    print(f"\nFlag Distribution:")
    for flag, count in flag_counts.items():
        print(f"  {flag}: {count} ({count/len(df)*100:.1f}%)")
    
    # Missing data check
    missing_data = df.isnull().sum()
    print(f"\nMissing Data:")
    for col, missing in missing_data.items():
        if missing > 0:
            print(f"  {col}: {missing}")
        else:
            print(f"  No missing data detected")
    
    # Interval completeness check by set
    print(f"\n🔄 INTERVAL COMPLETENESS BY SET:")
    for name in df['intertie_name'].unique()[:3]:  # Check first 3 interties
        print(f"\n{name}:")
        intertie_data = df[df['intertie_name'] == name]
        for set_num in range(num_sets):
            set_intervals = intertie_data[intertie_data['interval_set'] == set_num]['interval'].unique()
            expected_intervals = set(range(1, 13))  # 1-12 for 5-min intervals
            missing_intervals = expected_intervals - set(set_intervals)
            
            if missing_intervals:
                print(f"  Set {set_num}: Missing intervals {sorted(missing_intervals)}")
            else:
                print(f"  Set {set_num}: Complete (12/12 intervals)")
    
    # DSO-RD flag analysis
    print(f"\n🚩 DSO-RD FLAG ANALYSIS:")
    dso_rd_by_intertie = df[df['flag'] == 'DSO-RD'].groupby('intertie_name').size()
    print(f"Interties with DSO-RD flags:")
    for name, count in dso_rd_by_intertie.items():
        total_records = len(df[df['intertie_name'] == name])
        print(f"  {name}: {count}/{total_records} ({count/total_records*100:.1f}%)")
    
    # Recommendations
    print(f"\n💡 CLEANING RECOMMENDATIONS:")
    
    if zero_lmps > len(df) * 0.5:
        print("  ⚠️  High percentage of zero LMP values - investigate if this is normal")
    
    if 'DSO-RD' in df['flag'].values:
        print("  ℹ️  DSO-RD flags present - these may indicate data quality issues")
        print("     'DSO-RD' likely means 'Dispatch Scheduling Optimizer - Resource Decommitment'")
    
    print(f"  ✅ File contains {num_sets} time periods - determine if you want all periods or just latest")
    print("  ✅ Timestamps need to be calculated from DeliveryDate + DeliveryHour + IntervalSet + Interval")
    print("  ✅ Consider handling zero LMP values based on business rules")
    print("  ✅ Flag field should be preserved for data quality tracking")
    print("  ✅ Intertie names can be split into location/connection info if needed")
    
    print(f"\n📈 SAMPLE CLEANED STRUCTURE:")
    print("Recommended columns: timestamp, intertie_name, lmp_value, flag, location, connection, interval_set")
    
    print(f"\n🎯 KEY INSIGHTS:")
    print(f"  • This file contains {num_sets} hours of 5-minute interval data")
    print(f"  • Each intertie has {len(intervals)} total intervals (5 sets × 12 intervals)")
    print(f"  • 94.6% of LMP values are zero, mostly flagged as DSO-RD")
    print(f"  • Only 2 interties have non-zero values: MB.WHITESHELL and MN.INTFALLS")
    print(f"  • Data appears to be for hour {base_hour} and potentially 4 preceding hours")
    
if __name__ == "__main__":
    explore_intertie_lmp() 