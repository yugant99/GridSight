import duckdb 
import pandas as pd 
import glob 

conn = duckdb.connect("duckdb_analytics.db")

def create_tables():
    conn.execute("""
                 CREATE TABLE IF NOT EXISTS demand(
                 timestamp TIMESTAMP,
        ontario_demand_mw FLOAT
    );
    
                 CREATE TABLE IF NOT EXISTS zonal_demand(
                 timestamp TIMESTAMP,
                 zone_name VARCHAR(50),
        demand_mw FLOAT
    );
    
    CREATE TABLE IF NOT EXISTS genmix (
                 timestamp TIMESTAMP,
                 fuel_type VARCHAR(50),
        gen_mw FLOAT
    );
    
                 CREATE TABLE IF NOT EXISTS energy_lmp (
                 timestamp TIMESTAMP,
        delivery_hour VARCHAR(20),
                 interval INTEGER,
        pricing_location VARCHAR(100),
        lmp FLOAT,
        energy_loss_price FLOAT,
        energy_congestion_price FLOAT
    );
    
                 CREATE TABLE IF NOT EXISTS intertie_lmp(
                 timestamp TIMESTAMP,
        intertie_name VARCHAR(100),
                 location VARCHAR(10),
        connection VARCHAR(50),
        code VARCHAR(20),
        interval_set INTEGER,
        interval INTEGER,
                 lmp_value FLOAT,
        flag VARCHAR(20)
                 );
                 """)
    print("✅ Tables created successfully!")

if __name__ == "__main__":
    create_tables()