# Azure Live Scraper

Modular IESO data scraping system for Azure integration.

## 🚀 Quick Start

1. **Setup credentials**: Copy `config_template.py` to `config.py` and add your Azure credentials
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Run scraper**: `python energylmp_gap_filler.py`

## 📁 Structure

```
azure_live_scraper/
├── config_template.py      # Template for Azure credentials
├── scraper_utils.py         # Web scraping utilities
├── azure_utils.py           # Azure blob storage utilities
├── energylmp_gap_filler.py  # EnergyLMP scraper
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## 🎯 Features

- **Smart Gap Detection**: Automatically finds missing dates/versions
- **Version Management**: Downloads only latest versions
- **Azure Integration**: Direct upload to blob storage
- **Error Handling**: Robust error handling and reporting
- **Modular Design**: Easy to extend for new datasets

## 📊 Supported Datasets

- **EnergyLMP**: Hourly energy pricing data (CSV files)
- **IntertieLMP**: Cross-border electricity pricing (XML files)
- **GenMix**: Generation by fuel type (XML files)
- **Demand**: Provincial electricity demand (CSV files)
- **DemandZonal**: Zonal electricity demand (CSV files)

## 🛠️ Usage

### Individual Dataset Scraping
```bash
python energylmp_gap_filler.py      # Energy pricing
python intertielmp_gap_filler.py    # Cross-border pricing
python genmix_gap_filler.py         # Generation mix
```

### Comprehensive Scraping
```bash
python all_datasets_gap_filler.py   # All datasets at once
```

## 🔧 Configuration

1. Copy the template: `cp config_template.py config.py`
2. Edit `config.py` with your Azure credentials:
   ```python
   ACCOUNT_NAME = "your_storage_account"
   ACCOUNT_KEY = "your_storage_key"
   ```

## 🚀 Ready for Production

- Deploy to Azure Functions for daily automation
- Set up timer triggers for scheduled runs
- Monitor with Azure Application Insights
- Scale automatically based on data volume

**Cost**: <$10/month for complete live data pipeline 