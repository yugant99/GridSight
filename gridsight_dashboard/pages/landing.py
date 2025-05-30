import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

def show():
    """Landing page with pipeline explanation and navigation guide"""
    
    # Main header
    st.markdown('<h1 class="main-header">⚡ GridSight Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center; color: #7f8c8d; margin-bottom: 3rem;">Ontario Energy Market Data Collection & Analytics</h3>', unsafe_allow_html=True)
    
    # Pipeline explanation
    st.markdown('<div class="pipeline-box">', unsafe_allow_html=True)
    st.markdown("## 🔄 Data Pipeline Architecture")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("### 📡 IESO Scraper")
        st.markdown("- **Source**: Independent Electricity System Operator")
        st.markdown("- **Data**: Demand, Generation Mix, LMP, Zonal")
        st.markdown("- **Frequency**: Real-time scraping")
    
    with col2:
        st.markdown("### 🧹 Data Cleaner")
        st.markdown("- **Process**: Automated data cleaning")
        st.markdown("- **Validation**: Schema & quality checks")
        st.markdown("- **Output**: Standardized CSV files")
    
    with col3:
        st.markdown("### 🤖 ML Orchestrator")
        st.markdown("- **Models**: XGBoost + Random Forest")
        st.markdown("- **Predictions**: 24h demand forecasts")
        st.markdown("- **Schedule**: Daily at 2:00 PM EST")
    
    with col4:
        st.markdown("### 📊 Dashboard")
        st.markdown("- **Platform**: Streamlit")
        st.markdown("- **Connection**: Direct Azure integration")
        st.markdown("- **Updates**: Real-time data refresh")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Azure connection info
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("### ⚠️ Important Notice")
    st.markdown("**Azure Container Shutdown Date: May 29, 2025**")
    st.markdown("This dashboard is connected to the Azure ML Orchestrator running in production. The container will be shut down on the date above to manage costs.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Page descriptions
    st.markdown('<h2 class="page-header">📋 Dashboard Pages Overview</h2>', unsafe_allow_html=True)
    
    # Create cards for each page
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Demand Analysis")
        st.markdown("**What it shows:**")
        st.markdown("- Historical Ontario electricity demand patterns")
        st.markdown("- Interactive time-series visualizations") 
        st.markdown("- Seasonal and daily trend analysis")
        st.markdown("- Peak demand identification")
        st.markdown("- Filterable data tables with export options")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🤖 ML Predictions")
        st.markdown("**What it shows:**")
        st.markdown("- Live 24-hour demand forecasts")
        st.markdown("- Model performance metrics")
        st.markdown("- Prediction accuracy over time")
        st.markdown("- Grid stress detection alerts")
        st.markdown("- Feature importance analysis")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### ⚡ Generation Mix")
        st.markdown("**What it shows:**")
        st.markdown("- Electricity generation by fuel type")
        st.markdown("- Renewable vs non-renewable breakdown")
        st.markdown("- Generation capacity utilization")
        st.markdown("- Motion charts showing fuel transitions")
        st.markdown("- Interactive stacked area charts")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🗺️ Zonal Analysis")
        st.markdown("**What it shows:**")
        st.markdown("- Regional demand distribution")
        st.markdown("- Zone-by-zone comparison charts")
        st.markdown("- Geographic demand patterns")
        st.markdown("- Interactive zone selection")
        st.markdown("- Comparative analytics")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Technical specifications
    st.markdown('<h2 class="page-header">🔧 Technical Specifications</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 Data Sources")
        st.markdown("- **IESO Public Reports**")
        st.markdown("- **5 months** of historical data (Jan-May 2025)")
        st.markdown("- **Hourly** granularity")
        st.markdown("- **Real-time** updates via Azure")
    
    with col2:
        st.markdown("### 🤖 ML Models")
        st.markdown("- **XGBoost** for demand forecasting")
        st.markdown("- **Random Forest** for grid stress detection")
        st.markdown("- **MAE: 781.50 MW** (demand model)")
        st.markdown("- **92.5% accuracy** (stress detection)")
    
    with col3:
        st.markdown("### ☁️ Infrastructure")
        st.markdown("- **Azure Functions** for orchestration")
        st.markdown("- **Blob Storage** for data persistence")
        st.markdown("- **Streamlit Community Cloud** for dashboard")
        st.markdown("- **GitHub** for version control")
    
    # Footer
    st.markdown("---")
    st.markdown('<p style="text-align: center; color: #95a5a6;">Use the sidebar navigation to explore different data views and analytics</p>', unsafe_allow_html=True) 