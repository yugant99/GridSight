# GridSight ⚡

**Advanced Energy Market Data Pipeline & Analytics Platform**

GridSight is a comprehensive data science project that ingests, processes, and analyzes Ontario's electricity market data from the Independent Electricity System Operator (IESO). The platform provides insights into energy demand patterns, generator output, and locational marginal pricing across the Ontario electricity grid.

## 🎯 Project Overview

**Domain**: Energy Market Analysis & Grid Operations  
**Data Sources**: IESO Public Data  
**Architecture**: Cloud-based data lake with Azure Blob Storage  
**Timeline**: January 2025 - May 2025 (5 months of market data)  
**Scale**: 500,000+ time series records across multiple energy dimensions

## 📊 Current Project Status

✅ **Phase 1: Data Ingestion (COMPLETE)**  
✅ **Phase 2: Data Cleaning & Processing (COMPLETE)**  
🔄 **Phase 3: Database Integration (Next)**  
⏳ **Phase 4: Modeling & Analytics (Planned)**  
⏳ **Phase 5: Visualization & Insights (Planned)**

## 🔧 Setup & Configuration

### Prerequisites
```bash
pip install -r requirements.txt
```

### Azure Storage Setup
1. **Copy the configuration template**:
   ```bash
   cp config_template.py config.py
   ```

2. **Fill in your Azure credentials** in `config.py`:
   ```python
   ACCOUNT_NAME = "your_azure_storage_account"
   ACCOUNT_KEY = "your_azure_storage_key"
   ```

3. **Update placeholder values** in Python files:
   - Replace `YOUR_AZURE_STORAGE_ACCOUNT` with your account name
   - Replace `YOUR_AZURE_STORAGE_KEY_HERE` with your storage key

⚠️ **Security Note**: Never commit actual Azure credentials to version control. The `config.py` file is ignored by git.

## 🏗️ Data Architecture

### Raw Data Pipeline
```
IESO Public APIs → Azure Blob Storage ("raw-data") → Processing Scripts → Azure Blob Storage ("cleaned-data")
```

### Data Lake Structure
```
📁 raw-data/
├── 📁 Demand/year=2025/month=XX/day=XX/
├── 📁 ZonalDemand/year=2025/month=XX/day=XX/
├── 📁 GenMix/year=2025/month=XX/day=XX/
├── 📁 EnergyLMP/year=2025/month=XX/day=XX/
└── 📁 IntertieLMP/year=2025/month=XX/day=XX/

📁 cleaned-data/
├── 📁 Demand/year=2025/month=XX/day=XX/
├── 📁 ZonalDemand/year=2025/month=XX/day=XX/
├── 📁 GenMix/year=2025/month=XX/day=XX/
├── 📁 EnergyLMP/year=2025/month=XX/day=XX/
└── 📁 IntertieLMP/year=2025/month=XX/day=XX/
```

## 📈 Data Sources & Metrics

| Dataset | Format | Records | Time Period | Description |
|---------|--------|---------|-------------|-------------|
| **Demand** | CSV | ~36,000 | Jan-May 2025 | Provincial electricity demand (5-min intervals) |
| **ZonalDemand** | CSV | ~360,000 | Jan-May 2025 | Demand by transmission zone (5-min intervals) |
| **GenMix** | XML→CSV | ~21,000 | Jan-May 2025 | Generator output by fuel type (hourly) |
| **EnergyLMP** | CSV | ~36,000 | May 2025 | Locational marginal pricing (5-min intervals) |
| **IntertieLMP** | XML→CSV | ~25,000 | May 2025 | Intertie connection pricing (5-min intervals) |

## 🛠️ Technical Implementation

### Key Technologies
- **Cloud Storage**: Azure Blob Storage
- **Data Processing**: Python, Pandas, XML parsing
- **API Integration**: IESO Public Data APIs
- **Version Control**: Git/GitHub
- **Planned**: DuckDB, Machine Learning, Visualization

### Processing Pipeline Features
- **Memory-efficient processing**: Direct blob-to-blob transformation without local storage
- **Multi-format handling**: CSV and XML data processing
- **Timestamp standardization**: UTC timezone management
- **Data quality preservation**: Flag retention for quality tracking
- **Automated backfill**: Historical data ingestion with date filtering

## 📂 Project Structure

```
GridSight/
├── 📁 azure_push_clean/          # Data cleaning & upload scripts
│   ├── pub_demand_cleaned_push.py
│   ├── demand_zonal_clean_push.py
│   ├── genmix_clean_push.py
│   ├── energyLMP_clean_push.py
│   ├── intertielmp_push_clean.py
│   └── verify_intertie_cleaned.py
├── 📁 backfill_script_uncleaned/  # Raw data ingestion scripts
│   ├── backfill_demand.py
│   ├── backfill_zonal.py
│   ├── backfill_genmix.py
│   ├── backfill_energy_lmp.py
│   └── backfill_intertie_lmp.py
├── 📁 call_azure_cleanstep1/      # Download utilities
│   ├── call_demand.py
│   ├── call_genmix.py
│   ├── call_energylmp.py
│   └── call_intertie_lmp.py
├── 📁 data_explore/               # Data exploration & analysis
│   ├── pub_demand_explore.py
│   ├── Demand_Zonal_Explore.py
│   ├── GenMix_explore.py
│   ├── Energy_LMP_Explore.py
│   └── intertie_lmp_explore.py
├── 📁 lmp_cleaned/               # Local cleaned data cache
├── config_template.py            # Azure credentials template
├── project_roadmap.txt           # Detailed project roadmap
├── schema_1.txt                  # Database schema design
└── README.md                     # This file
```

## 🔍 Data Quality & Insights

### Processing Achievements
- **✅ 23/24 IntertieLMP files processed** (95.8% success rate)
- **✅ Multi-hour data handling** (5 hours per file, 1,080 records each)
- **✅ Timestamp accuracy** (5-minute interval precision)
- **✅ Geographic parsing** (18 intertie connections across 8 jurisdictions)

### Key Data Insights Discovered
- **IntertieLMP Analysis**: 94.6% of LMP values are zero (inactive connections)
- **Active Interties**: Only MB.WHITESHELL and MN.INTFALLS show consistent pricing
- **Jurisdictional Coverage**: Connections to Quebec (PQ), Manitoba (MB), New York (NY), Maryland (MD), Michigan (MI), Minnesota (MN), East Coast (EC), West Coast (WC)
- **Data Quality**: All records flagged as "DSO-RD" (Dispatch Scheduling Optimizer - Resource Decommitment)

## 🚀 Recent Accomplishments

### Data Ingestion Optimizations
- **Storage Efficiency**: Reduced data storage by ~97% through latest-daily-file selection
- **Fixed Timezone Issues**: Resolved datetime comparison errors in backfill scripts
- **XML Processing**: Successfully parsed complex GenMix and IntertieLMP XML structures
- **Memory Management**: Implemented direct blob-to-blob processing for large datasets

### Advanced Data Transformations
- **Timestamp Creation**: Calculated precise timestamps from delivery dates + intervals
- **Name Parsing**: Extracted location/connection info from intertie identifiers
- **Multi-format Support**: Unified CSV and XML data into consistent schemas
- **Quality Preservation**: Maintained data quality flags throughout processing

## 📋 Database Schema (Planned)

```sql
-- Demand Table
CREATE TABLE demand (
    timestamp TIMESTAMP,
    ontario_demand FLOAT,
    file_source VARCHAR(255)
);

-- ZonalDemand Table  
CREATE TABLE zonal_demand (
    timestamp TIMESTAMP,
    zone VARCHAR(50),
    demand FLOAT
);

-- GenMix Table
CREATE TABLE genmix (
    timestamp TIMESTAMP,
    fuel_type VARCHAR(50),
    energy_output FLOAT
);

-- EnergyLMP Table
CREATE TABLE energy_lmp (
    timestamp TIMESTAMP,
    interval INTEGER,
    lmp_value FLOAT
);

-- IntertieLMP Table
CREATE TABLE intertie_lmp (
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
```

## 🎯 Next Steps

### Phase 3: Database Integration
- [ ] Set up DuckDB for analytics
- [ ] Implement data ingestion from cleaned blobs
- [ ] Create joined tables for cross-dataset analysis
- [ ] Build automated data quality checks

### Phase 4: Advanced Analytics
- [ ] Demand forecasting models
- [ ] Intertie flow analysis
- [ ] Price correlation studies
- [ ] Generator efficiency analysis

### Phase 5: Visualization & Insights
- [ ] Interactive dashboards
- [ ] Time series visualizations
- [ ] Geographic grid mapping
- [ ] Real-time monitoring capabilities

## 🔧 Running Data Processing

### Clean and upload specific dataset
```bash
python azure_push_clean/intertielmp_push_clean.py
```

### Explore data structure
```bash
python data_explore/intertie_lmp_explore.py
```

## 📊 Project Metrics

- **📈 Data Volume**: 500,000+ time series records
- **🌐 Geographic Coverage**: 8 jurisdiction connections  
- **⏱️ Temporal Resolution**: 5-minute intervals
- **📅 Historical Depth**: 5 months (Jan-May 2025)
- **☁️ Cloud Architecture**: 100% Azure-based data lake
- **🔄 Processing Efficiency**: 95%+ success rate

## 🤝 Contributing

This project demonstrates advanced data engineering practices in the energy sector. Key learning areas include:
- Complex multi-format data integration
- Cloud-native data pipeline design
- Energy market domain expertise
- Time series data management
- Azure blob storage optimization

## 📜 License

This project is for educational and research purposes, utilizing publicly available IESO data.

---

**GridSight** - *Illuminating Ontario's Energy Market Through Data Science*

🔗 **Data Source**: [IESO Public Data](http://reports.ieso.ca/)  
📧 **Contact**: [GitHub Issues](https://github.com/yugant99/GridSight/issues) 