import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# Import page modules
from pages import landing, demand_analysis, genmix_analysis, ml_predictions, zonal_analysis, intertie_lmp_analysis, energy_lmp_analysis
from utils.data_loader import load_data_from_azure
from utils.azure_config import get_azure_config

# Page configuration
st.set_page_config(
    page_title="GridSight - Ontario Energy Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for minimal, clean styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    .page-header {
        font-size: 2rem;
        color: #2c3e50;
        margin-bottom: 1rem;
        border-bottom: 2px solid #ecf0f1;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .pipeline-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Sidebar navigation
    st.sidebar.title("⚡ GridSight Navigation")
    
    # Add connection status
    st.sidebar.markdown("---")
    
    try:
        # Test Azure connection
        azure_config = get_azure_config()
        st.sidebar.success("🟢 Connected to Azure")
        st.sidebar.info(f"Storage: {azure_config['account_name']}")
    except Exception as e:
        st.sidebar.error("🔴 Azure Connection Error")
        st.sidebar.error(str(e))
    
    st.sidebar.markdown("---")
    
    # Page selection
    pages = {
        "🏠 Home": landing,
        "📊 Demand Analysis": demand_analysis,
        "⚡ Generation Mix": genmix_analysis,
        "🤖 ML Predictions": ml_predictions,
        "🗺️ Zonal Analysis": zonal_analysis,
        "🔗 Intertie LMP Analysis": intertie_lmp_analysis,
        "💰 Energy LMP Analysis": energy_lmp_analysis
    }
    
    selected_page = st.sidebar.radio("Select Page", list(pages.keys()))
    
    # Pipeline status
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔄 Pipeline Status")
    st.sidebar.info("📅 **Container Shutdown:** May 29, 2025")
    st.sidebar.warning("⏰ **Daily Updates:** 2:00 PM EST")
    
    # Load and display selected page
    try:
        pages[selected_page].show()
    except Exception as e:
        st.error(f"Error loading page: {str(e)}")
        st.info("Please check your Azure connection and try again.")

if __name__ == "__main__":
    main() 