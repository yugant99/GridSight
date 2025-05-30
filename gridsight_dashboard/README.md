# 🌟 GridSight Analytics Dashboard

**Ontario Energy Market Data Collection & Analytics Dashboard**

A comprehensive, interactive Streamlit dashboard for analyzing Ontario's electricity market data, featuring live ML predictions and beautiful visualizations.

![Dashboard Preview](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Azure](https://img.shields.io/badge/Azure-0078D4?style=for-the-badge&logo=microsoft-azure&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## 🚀 Features

### 📊 **Multi-Page Analytics**
- **Landing Page**: Pipeline overview and navigation guide
- **Demand Analysis**: Historical electricity demand patterns with interactive filters
- **Generation Mix**: Fuel type analysis with motion charts and stacked visualizations
- **ML Predictions**: Live 24-hour forecasts and model performance metrics
- **Zonal Analysis**: Regional demand distribution and geographic patterns

### 🎯 **Interactive Elements**
- ✅ **Filterable Tables**: User-selectable filters for all datasets
- ✅ **Motion Charts**: Animated fuel transition visualizations
- ✅ **Real-time Data**: Direct Azure blob storage integration
- ✅ **Export Options**: CSV/JSON download capabilities
- ✅ **Responsive Design**: Clean, minimal interface

### 🤖 **ML Integration**
- Live demand forecasting (XGBoost model)
- Grid stress detection (Random Forest)
- Model performance tracking
- Feature importance analysis

## 🏗️ Architecture

```
IESO Data → Azure Scraper → Data Cleaner → ML Orchestrator → Dashboard
    ↓              ↓             ↓              ↓            ↓
Raw Data → Cleaned CSV → ML Models → Predictions → Visualizations
```

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- Azure Storage Account access
- Git

### Local Development

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd gridsight_dashboard
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up Azure credentials**

**Option 1: Environment Variables**
```bash
export AZURE_STORAGE_ACCOUNT_NAME="datastoreyugant"
export AZURE_STORAGE_ACCOUNT_KEY="your_azure_key_here"
```

**Option 2: Streamlit Secrets (Recommended for deployment)**
Create `.streamlit/secrets.toml`:
```toml
[azure]
account_name = "datastoreyugant"
account_key = "your_azure_key_here"
```

4. **Run the dashboard**
```bash
streamlit run main.py
```

## 🌐 Deployment

### Streamlit Community Cloud (Recommended)

1. **Push to GitHub**
```bash
git add .
git commit -m "Add GridSight Dashboard"
git push origin main
```

2. **Deploy to Streamlit Cloud**
- Visit [share.streamlit.io](https://share.streamlit.io)
- Connect your GitHub repository
- Select `gridsight_dashboard/main.py` as the main file
- Add Azure credentials in the Secrets section:
```toml
[azure]
account_name = "datastoreyugant"
account_key = "your_azure_key_here"
```

3. **Access your dashboard**
Your dashboard will be available at: `https://yourapp.streamlit.app`

### Alternative Deployment Options

#### Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Heroku
Add `Procfile`:
```
web: sh setup.sh && streamlit run main.py
```

## 📊 Data Sources

- **IESO (Independent Electricity System Operator)**
  - Electricity demand data
  - Generation mix by fuel type
  - Zonal demand patterns
  - Real-time market data

- **Azure ML Orchestrator**
  - XGBoost demand forecasting
  - Random Forest grid stress detection
  - Model performance metrics

## 🎛️ Configuration

### Environment Variables
- `AZURE_STORAGE_ACCOUNT_NAME`: Azure storage account name
- `AZURE_STORAGE_ACCOUNT_KEY`: Azure storage access key

### Data Containers
- `cleaned-data`: Processed CSV files
- `ml-outputs`: ML predictions and model summaries
- `raw-data`: Original IESO data files

## 📈 Usage Guide

### Navigation
Use the sidebar to navigate between different analysis pages:

1. **🏠 Home**: Overview and pipeline explanation
2. **📊 Demand Analysis**: Filter and analyze electricity demand
3. **⚡ Generation Mix**: Explore fuel type distributions
4. **🤖 ML Predictions**: View live forecasts and model performance
5. **🗺️ Zonal Analysis**: Regional demand patterns

### Filters
- **Date Range**: Select specific time periods
- **Hours**: Filter by hour of day (0-23)
- **Days of Week**: Weekend vs weekday analysis
- **Fuel Types**: Select specific generation sources
- **Zones**: Choose geographic regions

### Export Options
- Download filtered data as CSV
- Export summary statistics
- Save ML predictions as JSON

## 🔧 Technical Specifications

### Dependencies
- **Streamlit**: Web application framework
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation
- **Azure Storage**: Cloud data access
- **NumPy**: Numerical computations

### Performance
- **Caching**: 1-hour cache for data, 30-min for ML predictions
- **Lazy Loading**: Data loaded only when needed
- **Responsive**: Optimized for desktop and mobile

## ⚠️ Important Notes

- **Container Shutdown**: Azure container shuts down on **May 29, 2025**
- **Data Updates**: ML models retrain daily at 2:00 PM EST
- **Cache Refresh**: Use sidebar refresh button for latest data

## 🎨 Customization

### Styling
Modify CSS in `main.py` for custom themes:
```python
st.markdown("""
<style>
    .main-header { color: #1f77b4; }
    .metric-card { background: #f8f9fa; }
</style>
""", unsafe_allow_html=True)
```

### Adding New Pages
1. Create new file in `pages/` directory
2. Add `show()` function
3. Import and add to `main.py` pages dictionary

## 🐛 Troubleshooting

### Common Issues

**Azure Connection Error**
- Verify storage account name and key
- Check network connectivity
- Ensure containers exist

**Data Loading Issues**
- Clear cache using sidebar refresh button
- Check Azure blob storage permissions
- Verify file naming conventions

**Performance Issues**
- Reduce date range filters
- Limit number of selected zones/fuels
- Check internet connection

## 📞 Support

For issues and questions:
- Check Azure connection status in sidebar
- Review error messages in dashboard
- Verify Azure storage permissions

## 📝 License

This project is part of the GridSight Analytics platform for Ontario energy market analysis.

---

**Built with ❤️ using Streamlit and Azure** 