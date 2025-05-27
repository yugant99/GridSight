#!/usr/bin/env python3
"""
All Datasets Gap Filler
Runs gap filling for all IESO datasets in sequence
"""

import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Import all gap fillers
    from energylmp_gap_filler import scrape_energylmp_gap
    from intertielmp_gap_filler import scrape_intertielmp_gap
    from genmix_gap_filler import scrape_genmix_gap
    from demand_gap_filler import scrape_demand_gap
    from demandzone_gap_filler import scrape_demandzone_gap
except ImportError:
    print("❌ Error: Please copy config_template.py to config.py and add your Azure credentials")
    sys.exit(1)

def run_all_gap_fillers():
    """Run all dataset gap fillers in sequence"""
    print("🚀 Starting comprehensive gap filling for all IESO datasets...")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {}
    
    # Dataset configurations
    datasets = [
        {
            'name': 'EnergyLMP',
            'function': scrape_energylmp_gap,
            'description': 'Hourly energy pricing data (CSV)',
            'priority': 1
        },
        {
            'name': 'IntertieLMP', 
            'function': scrape_intertielmp_gap,
            'description': 'Cross-border pricing data (XML)',
            'priority': 2
        },
        {
            'name': 'GenMix',
            'function': scrape_genmix_gap,
            'description': 'Generation by fuel type (XML)',
            'priority': 3
        },
        {
            'name': 'Demand',
            'function': scrape_demand_gap,
            'description': 'Provincial demand data (CSV)',
            'priority': 4
        },
        {
            'name': 'DemandZonal',
            'function': scrape_demandzone_gap,
            'description': 'Zonal demand data (CSV)',
            'priority': 5
        }
    ]
    
    # Sort by priority
    datasets.sort(key=lambda x: x['priority'])
    
    total_files = 0
    
    for dataset in datasets:
        print(f"\n📊 DATASET: {dataset['name']}")
        print(f"📝 Description: {dataset['description']}")
        print("-" * 40)
        
        try:
            files_processed = dataset['function']()
            results[dataset['name']] = {
                'status': 'success',
                'files_processed': files_processed,
                'error': None
            }
            total_files += files_processed
            
            if files_processed > 0:
                print(f"✅ {dataset['name']}: {files_processed} files processed")
            else:
                print(f"✅ {dataset['name']}: Up to date")
                
        except Exception as e:
            print(f"❌ {dataset['name']}: Error - {e}")
            results[dataset['name']] = {
                'status': 'error',
                'files_processed': 0,
                'error': str(e)
            }
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 COMPREHENSIVE GAP FILLING SUMMARY")
    print("=" * 60)
    
    success_count = 0
    error_count = 0
    
    for dataset_name, result in results.items():
        status_icon = "✅" if result['status'] == 'success' else "❌"
        files_text = f"{result['files_processed']} files" if result['files_processed'] > 0 else "up to date"
        
        print(f"{status_icon} {dataset_name:12} | {files_text}")
        
        if result['status'] == 'success':
            success_count += 1
        else:
            error_count += 1
            print(f"   Error: {result['error']}")
    
    print("-" * 60)
    print(f"📊 Total files processed: {total_files}")
    print(f"✅ Successful datasets: {success_count}/{len(datasets)}")
    print(f"❌ Failed datasets: {error_count}/{len(datasets)}")
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if total_files > 0:
        print(f"\n📋 NEXT STEPS:")
        print(f"1. Run cleaning scripts for updated datasets")
        print(f"2. Verify Synapse external tables see new data")
        print(f"3. Update ML models with fresh data")
        print(f"4. Set up daily automation for ongoing updates")
    
    return results

def main():
    """Main entry point"""
    try:
        results = run_all_gap_fillers()
        
        # Exit with error code if any dataset failed
        failed_datasets = [name for name, result in results.items() if result['status'] == 'error']
        if failed_datasets:
            print(f"\n⚠️  Some datasets failed: {', '.join(failed_datasets)}")
            sys.exit(1)
        else:
            print(f"\n🎉 All datasets processed successfully!")
            sys.exit(0)
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 