import duckdb
import glob

conn = duckdb.connect('duckdb_analytics.db')

def load_energy_lmp_files():
    energy_files = glob.glob('data/energy_lmp/*.csv')
    print(f"📥 Loading {len(energy_files)} Energy LMP files")

    for file in energy_files:
        print(f"Loading {file}")

        conn.execute(f"""
            INSERT INTO energy_lmp
            SELECT timestamp::TIMESTAMP, delivery_hour, interval, pricing_location, 
                   lmp, energy_loss_price, energy_congestion_price
            FROM read_csv_auto('{file}')
        """)
    
    count = conn.execute('SELECT COUNT(*) FROM energy_lmp').fetchone()[0]
    print(f"✅ EnergyLMP loaded: {count:,} records")

def load_intertie_lmp_files():
    intertie_files = glob.glob('data/intertie_lmp/*.csv')
    print(f"📥 Loading {len(intertie_files)} Intertie LMP files")

    for file in intertie_files:
        print(f"Loading {file}")

        conn.execute(f"""
            INSERT INTO intertie_lmp
            SELECT timestamp::TIMESTAMP, intertie_name, location, connection, 
                   code, interval_set, interval, lmp_value, flag
            FROM read_csv_auto('{file}')
        """)
    
    count = conn.execute("SELECT COUNT(*) FROM intertie_lmp").fetchone()[0]
    print(f"✅ IntertieLMP loaded: {count:,} records")

if __name__ == "__main__":
    load_energy_lmp_files()
    load_intertie_lmp_files()