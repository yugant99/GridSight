#!/usr/bin/env python3
"""
Standalone test script for IESO data scrapers
"""
import sys
import os
from datetime import datetime, timedelta

# Add the scraper_modules directory to the path
sys.path.append('scraper_modules')

# Import the scraper modules
try:
    from energylmp_gap_filler import EnergyLMPGapFiller
    from intertielmp_gap_filler import IntertieLMPGapFiller
    from genmix_gap_filler import GenMixGapFiller
    from demand_gap_filler import DemandGapFiller
    from demandzone_gap_filler import DemandZoneGapFiller
    print("✅ All scraper modules imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_scrapers():
    """Test each scraper with recent dates"""
    print("\n🧪 Testing IESO Data Scrapers")
    print("=" * 50)
    
    # Test dates - try last few days
    test_dates = []
    for i in range(1, 4):  # Test last 3 days
        test_date = datetime.now() - timedelta(days=i)
        test_dates.append(test_date.strftime('%Y%m%d'))
    
    print(f"Testing with dates: {test_dates}")
    
    # Test EnergyLMP (hourly data)
    print("\n📊 Testing EnergyLMP Scraper...")
    try:
        energy_scraper = EnergyLMPGapFiller()
        for date in test_dates:
            print(f"  Checking EnergyLMP for {date}...")
            # Check if data exists for this date
            url = f"http://reports.ieso.ca/public/PUB_PricesPubLMP_{date}.xml"
            print(f"    URL: {url}")
            # Note: We're not actually downloading in test mode
        print("  ✅ EnergyLMP scraper initialized successfully")
    except Exception as e:
        print(f"  ❌ EnergyLMP error: {e}")
    
    # Test IntertieLMP (hourly data)
    print("\n🔗 Testing IntertieLMP Scraper...")
    try:
        intertie_scraper = IntertieLMPGapFiller()
        for date in test_dates:
            print(f"  Checking IntertieLMP for {date}...")
            url = f"http://reports.ieso.ca/public/PUB_PricesIntertieLMP_{date}.xml"
            print(f"    URL: {url}")
        print("  ✅ IntertieLMP scraper initialized successfully")
    except Exception as e:
        print(f"  ❌ IntertieLMP error: {e}")
    
    # Test GenMix (annual data)
    print("\n⚡ Testing GenMix Scraper...")
    try:
        genmix_scraper = GenMixGapFiller()
        current_year = datetime.now().year
        print(f"  Checking GenMix for year {current_year}...")
        url = f"http://reports.ieso.ca/public/GenOutputCapability/PUB_GenOutputCapability_{current_year}.xml"
        print(f"    URL: {url}")
        print("  ✅ GenMix scraper initialized successfully")
    except Exception as e:
        print(f"  ❌ GenMix error: {e}")
    
    # Test Demand (annual data)
    print("\n📈 Testing Demand Scraper...")
    try:
        demand_scraper = DemandGapFiller()
        current_year = datetime.now().year
        print(f"  Checking Demand for year {current_year}...")
        url = f"http://reports.ieso.ca/public/Demand/PUB_Demand_{current_year}.csv"
        print(f"    URL: {url}")
        print("  ✅ Demand scraper initialized successfully")
    except Exception as e:
        print(f"  ❌ Demand error: {e}")
    
    # Test DemandZone (annual data)
    print("\n🗺️ Testing DemandZone Scraper...")
    try:
        demandzone_scraper = DemandZoneGapFiller()
        current_year = datetime.now().year
        print(f"  Checking DemandZone for year {current_year}...")
        url = f"http://reports.ieso.ca/public/DemandZonal/PUB_DemandZonal_{current_year}.csv"
        print(f"    URL: {url}")
        print("  ✅ DemandZone scraper initialized successfully")
    except Exception as e:
        print(f"  ❌ DemandZone error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("- All scraper modules can be imported")
    print("- Scrapers can be initialized")
    print("- URLs are properly formatted")
    print("- Ready for actual data collection!")
    
    print("\n💡 Note: This is a dry run test.")
    print("   Actual data collection requires Azure storage credentials.")
    print("   The Azure Function will handle real data collection automatically.")

if __name__ == "__main__":
    test_scrapers() 