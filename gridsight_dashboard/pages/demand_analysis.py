import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from utils.data_loader import load_demand_data, refresh_cache

def show():
    """Demand Analysis page with interactive charts and tables"""
    
    st.markdown('<h1 class="page-header">📊 Ontario Electricity Demand Analysis</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading demand data from Azure..."):
        demand_data = load_demand_data()
    
    if demand_data is None:
        st.error("❌ Unable to load demand data. Please check your Azure connection.")
        return
    
    # Data preprocessing
    demand_data['timestamp'] = pd.to_datetime(demand_data['timestamp'])
    demand_data['Date'] = demand_data['timestamp'].dt.date
    demand_data['Hour'] = demand_data['timestamp'].dt.hour
    demand_data['Day_of_Week'] = demand_data['timestamp'].dt.day_name()
    demand_data['Month'] = demand_data['timestamp'].dt.month_name()
    
    # Sidebar filters
    st.sidebar.markdown("### 🎛️ Data Filters")
    
    # Date range filter
    min_date = demand_data['Date'].min()
    max_date = demand_data['Date'].max()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Hour filter
    hours = st.sidebar.multiselect(
        "Select Hours (0-23)",
        options=list(range(24)),
        default=list(range(24))
    )
    
    # Day of week filter
    days = st.sidebar.multiselect(
        "Select Days of Week",
        options=demand_data['Day_of_Week'].unique(),
        default=demand_data['Day_of_Week'].unique()
    )
    
    # Month filter
    months = st.sidebar.multiselect(
        "Select Months",
        options=demand_data['Month'].unique(),
        default=demand_data['Month'].unique()
    )
    
    # Apply filters
    if len(date_range) == 2:
        filtered_data = demand_data[
            (demand_data['Date'] >= date_range[0]) &
            (demand_data['Date'] <= date_range[1]) &
            (demand_data['Hour'].isin(hours)) &
            (demand_data['Day_of_Week'].isin(days)) &
            (demand_data['Month'].isin(months))
        ]
    else:
        filtered_data = demand_data[
            (demand_data['Hour'].isin(hours)) &
            (demand_data['Day_of_Week'].isin(days)) &
            (demand_data['Month'].isin(months))
        ]
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        refresh_cache()
        st.experimental_rerun()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_demand = filtered_data['Ontario Demand'].mean()
        st.metric("Average Demand", f"{avg_demand:,.0f} MW")
    
    with col2:
        max_demand = filtered_data['Ontario Demand'].max()
        st.metric("Peak Demand", f"{max_demand:,.0f} MW")
    
    with col3:
        min_demand = filtered_data['Ontario Demand'].min()
        st.metric("Minimum Demand", f"{min_demand:,.0f} MW")
    
    with col4:
        std_demand = filtered_data['Ontario Demand'].std()
        st.metric("Volatility (σ)", f"{std_demand:,.0f} MW")
    
    # Main visualizations
    st.markdown("### 📈 Time Series Analysis")
    
    # Time series plot
    fig_ts = px.line(
        filtered_data, 
        x='timestamp', 
        y='Ontario Demand',
        title='Ontario Electricity Demand Over Time',
        labels={'Ontario Demand': 'Demand (MW)', 'timestamp': 'Date & Time'}
    )
    fig_ts.update_layout(height=500, showlegend=False)
    fig_ts.update_traces(line=dict(color='#1f77b4', width=1))
    st.plotly_chart(fig_ts, use_container_width=True)
    
    # Daily patterns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⏰ Daily Patterns")
        hourly_avg = filtered_data.groupby('Hour')['Ontario Demand'].mean().reset_index()
        
        fig_hourly = px.bar(
            hourly_avg,
            x='Hour',
            y='Ontario Demand',
            title='Average Demand by Hour of Day',
            color='Ontario Demand',
            color_continuous_scale='viridis'
        )
        fig_hourly.update_layout(height=400)
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    with col2:
        st.markdown("### 📅 Weekly Patterns")
        daily_avg = filtered_data.groupby('Day_of_Week')['Ontario Demand'].mean().reset_index()
        
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_avg['Day_of_Week'] = pd.Categorical(daily_avg['Day_of_Week'], categories=day_order, ordered=True)
        daily_avg = daily_avg.sort_values('Day_of_Week')
        
        fig_daily = px.bar(
            daily_avg,
            x='Day_of_Week',
            y='Ontario Demand',
            title='Average Demand by Day of Week',
            color='Ontario Demand',
            color_continuous_scale='plasma'
        )
        fig_daily.update_layout(height=400)
        st.plotly_chart(fig_daily, use_container_width=True)
    
    # Monthly trends
    st.markdown("### 📊 Monthly Trends")
    monthly_stats = filtered_data.groupby('Month')['Ontario Demand'].agg(['mean', 'max', 'min']).reset_index()
    
    fig_monthly = go.Figure()
    fig_monthly.add_trace(go.Scatter(x=monthly_stats['Month'], y=monthly_stats['mean'], 
                                   mode='lines+markers', name='Average', line=dict(color='blue')))
    fig_monthly.add_trace(go.Scatter(x=monthly_stats['Month'], y=monthly_stats['max'], 
                                   mode='lines+markers', name='Peak', line=dict(color='red')))
    fig_monthly.add_trace(go.Scatter(x=monthly_stats['Month'], y=monthly_stats['min'], 
                                   mode='lines+markers', name='Minimum', line=dict(color='green')))
    
    fig_monthly.update_layout(
        title='Monthly Demand Statistics',
        xaxis_title='Month',
        yaxis_title='Demand (MW)',
        height=500
    )
    st.plotly_chart(fig_monthly, use_container_width=True)
    
    # Interactive data table
    st.markdown("### 📋 Interactive Data Table")
    
    # Table options
    col1, col2, col3 = st.columns(3)
    with col1:
        table_rows = st.selectbox("Rows to display", [50, 100, 500, 1000], index=1)
    with col2:
        sort_column = st.selectbox("Sort by", ['timestamp', 'Ontario Demand', 'Hour', 'Day_of_Week'])
    with col3:
        sort_order = st.selectbox("Sort order", ['Ascending', 'Descending'])
    
    # Prepare table data
    table_data = filtered_data[['timestamp', 'Ontario Demand', 'Hour', 'Day_of_Week', 'Month']].copy()
    
    # Sort data
    ascending = sort_order == 'Ascending'
    table_data = table_data.sort_values(sort_column, ascending=ascending)
    
    # Display table
    st.dataframe(
        table_data.head(table_rows),
        use_container_width=True,
        height=400
    )
    
    # Download options
    st.markdown("### 💾 Export Data")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Download Filtered Data (CSV)"):
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"ontario_demand_{date_range[0]}_{date_range[1] if len(date_range)==2 else datetime.now().date()}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📈 Download Summary Statistics"):
            summary = filtered_data['Ontario Demand'].describe().to_frame()
            csv_summary = summary.to_csv()
            st.download_button(
                label="Download Summary",
                data=csv_summary,
                file_name=f"demand_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # Data info
    st.markdown("---")
    st.markdown(f"**Data Summary:** Showing {len(filtered_data):,} records from {filtered_data['timestamp'].min()} to {filtered_data['timestamp'].max()}") 