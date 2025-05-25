# scripts/load_single_datasets.py
import duckdb
import glob
import os

conn = duckdb.connect('duckdb_analytics.db')

def load_single_csv_datasets():
    # Load demand (single file) - it's in pub_demand directory
    # Columns: Date,Hour,Market Demand,Ontario Demand,timestamp
    demand_file = glob.glob('data/pub_demand/*.csv')[0]
    print(f"📥 Loading demand from: {demand_file}")
    conn.execute(f"""
        INSERT INTO demand 
        SELECT timestamp::TIMESTAMP, "Ontario Demand" as ontario_demand_mw
        FROM read_csv_auto('{demand_file}')
    """)
    
    # Load zonal demand (single file) - it's in demandzonal directory  
    # This has multiple zone columns, we need to unpivot it
    zonal_file = glob.glob('data/demandzonal/*.csv')[0]
    print(f"📥 Loading zonal demand from: {zonal_file}")
    conn.execute(f"""
        INSERT INTO zonal_demand
        SELECT timestamp::TIMESTAMP, 'Northwest' as zone_name, Northwest as demand_mw FROM read_csv_auto('{zonal_file}') WHERE Northwest IS NOT NULL
        UNION ALL
        SELECT timestamp::TIMESTAMP, 'Northeast' as zone_name, Northeast as demand_mw FROM read_csv_auto('{zonal_file}') WHERE Northeast IS NOT NULL
        UNION ALL  
        SELECT timestamp::TIMESTAMP, 'Ottawa' as zone_name, Ottawa as demand_mw FROM read_csv_auto('{zonal_file}') WHERE Ottawa IS NOT NULL
        UNION ALL
        SELECT timestamp::TIMESTAMP, 'East' as zone_name, East as demand_mw FROM read_csv_auto('{zonal_file}') WHERE East IS NOT NULL
        UNION ALL
        SELECT timestamp::TIMESTAMP, 'Toronto' as zone_name, Toronto as demand_mw FROM read_csv_auto('{zonal_file}') WHERE Toronto IS NOT NULL
        UNION ALL
        SELECT timestamp::TIMESTAMP, 'Essa' as zone_name, Essa as demand_mw FROM read_csv_auto('{zonal_file}') WHERE Essa IS NOT NULL
        UNION ALL
        SELECT timestamp::TIMESTAMP, 'Bruce' as zone_name, Bruce as demand_mw FROM read_csv_auto('{zonal_file}') WHERE Bruce IS NOT NULL
        UNION ALL
        SELECT timestamp::TIMESTAMP, 'Southwest' as zone_name, Southwest as demand_mw FROM read_csv_auto('{zonal_file}') WHERE Southwest IS NOT NULL
        UNION ALL
        SELECT timestamp::TIMESTAMP, 'Niagara' as zone_name, Niagara as demand_mw FROM read_csv_auto('{zonal_file}') WHERE Niagara IS NOT NULL
        UNION ALL
        SELECT timestamp::TIMESTAMP, 'West' as zone_name, West as demand_mw FROM read_csv_auto('{zonal_file}') WHERE West IS NOT NULL
    """)
    
    # Load genmix (single file)
    # Columns: timestamp,fuel,output
    genmix_file = glob.glob('data/genmix/*.csv')[0]
    print(f"📥 Loading genmix from: {genmix_file}")
    conn.execute(f"""
        INSERT INTO genmix
        SELECT timestamp::TIMESTAMP, fuel as fuel_type, output as gen_mw
        FROM read_csv_auto('{genmix_file}')
    """)
    
    print("✅ Single datasets loaded!")
    
    # Quick verification
    print("📊 Record counts:")
    print(f"Demand: {conn.execute('SELECT COUNT(*) FROM demand').fetchone()[0]:,}")
    print(f"Zonal: {conn.execute('SELECT COUNT(*) FROM zonal_demand').fetchone()[0]:,}")
    print(f"GenMix: {conn.execute('SELECT COUNT(*) FROM genmix').fetchone()[0]:,}")

if __name__ == "__main__":
    load_single_csv_datasets()