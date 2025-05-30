import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from utils.data_loader import load_genmix_data, refresh_cache

def show():
    """Generation Mix Analysis page with motion charts and interactive visualizations"""
    
    st.markdown('<h1 class="page-header">⚡ Ontario Generation Mix Analysis</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading generation mix data from Azure..."):
        genmix_data = load_genmix_data()
    
    if genmix_data is None:
        st.error("❌ Unable to load generation mix data. Please check your Azure connection.")
        return
    
    # Data preprocessing
    genmix_data['timestamp'] = pd.to_datetime(genmix_data['timestamp'])
    genmix_data['Date'] = genmix_data['timestamp'].dt.date
    genmix_data['Hour'] = genmix_data['timestamp'].dt.hour
    genmix_data['Day_of_Week'] = genmix_data['timestamp'].dt.day_name()
    genmix_data['Month'] = genmix_data['timestamp'].dt.month_name()
    
    # Get fuel type columns (excluding timestamp and derived columns)
    fuel_columns = [col for col in genmix_data.columns if col not in ['timestamp', 'Date', 'Hour', 'Day_of_Week', 'Month']]
    
    # Sidebar filters
    st.sidebar.markdown("### 🎛️ Data Filters")
    
    # Date range filter
    min_date = genmix_data['Date'].min()
    max_date = genmix_data['Date'].max()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Fuel type filter
    selected_fuels = st.sidebar.multiselect(
        "Select Fuel Types",
        options=fuel_columns,
        default=fuel_columns
    )
    
    # Hour filter
    hours = st.sidebar.multiselect(
        "Select Hours (0-23)",
        options=list(range(24)),
        default=list(range(24))
    )
    
    # Apply filters
    if len(date_range) == 2:
        filtered_data = genmix_data[
            (genmix_data['Date'] >= date_range[0]) &
            (genmix_data['Date'] <= date_range[1]) &
            (genmix_data['Hour'].isin(hours))
        ]
    else:
        filtered_data = genmix_data[genmix_data['Hour'].isin(hours)]
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        refresh_cache()
        st.experimental_rerun()
    
    # Calculate totals and percentages
    filtered_data['Total_Generation'] = filtered_data[selected_fuels].sum(axis=1)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_gen = filtered_data['Total_Generation'].mean()
        st.metric("Avg Total Generation", f"{total_gen:,.0f} MW")
    
    with col2:
        max_gen = filtered_data['Total_Generation'].max()
        st.metric("Peak Generation", f"{max_gen:,.0f} MW")
    
    with col3:
        # Calculate renewable percentage (assuming these are renewable)
        renewable_fuels = [col for col in selected_fuels if any(renewable in col.lower() 
                          for renewable in ['hydro', 'wind', 'solar', 'biomass', 'nuclear'])]
        if renewable_fuels:
            renewable_pct = (filtered_data[renewable_fuels].sum(axis=1) / filtered_data['Total_Generation'] * 100).mean()
            st.metric("Avg Renewable %", f"{renewable_pct:.1f}%")
        else:
            st.metric("Renewable %", "N/A")
    
    with col4:
        # Most dominant fuel
        avg_by_fuel = filtered_data[selected_fuels].mean()
        dominant_fuel = avg_by_fuel.idxmax()
        st.metric("Dominant Fuel", dominant_fuel.replace('_', ' '))
    
    # Main visualizations
    st.markdown("### 📊 Generation Mix Overview")
    
    # Stacked area chart
    fig_area = go.Figure()
    
    colors = px.colors.qualitative.Set3
    for i, fuel in enumerate(selected_fuels):
        fig_area.add_trace(go.Scatter(
            x=filtered_data['timestamp'],
            y=filtered_data[fuel],
            mode='lines',
            stackgroup='one',
            name=fuel.replace('_', ' '),
            line=dict(width=0),
            fillcolor=colors[i % len(colors)]
        ))
    
    fig_area.update_layout(
        title='Generation Mix Over Time (Stacked Area)',
        xaxis_title='Date & Time',
        yaxis_title='Generation (MW)',
        height=500,
        hovermode='x unified'
    )
    st.plotly_chart(fig_area, use_container_width=True)
    
    # Fuel type comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔥 Average Generation by Fuel Type")
        fuel_avg = filtered_data[selected_fuels].mean().sort_values(ascending=True)
        
        fig_bar = px.bar(
            x=fuel_avg.values,
            y=[name.replace('_', ' ') for name in fuel_avg.index],
            orientation='h',
            title='Average Generation by Fuel Type',
            color=fuel_avg.values,
            color_continuous_scale='viridis'
        )
        fig_bar.update_layout(height=400, showlegend=False)
        fig_bar.update_xaxis(title="Average Generation (MW)")
        fig_bar.update_yaxis(title="Fuel Type")
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        st.markdown("### 🥧 Generation Mix Distribution")
        fuel_totals = filtered_data[selected_fuels].sum()
        
        fig_pie = px.pie(
            values=fuel_totals.values,
            names=[name.replace('_', ' ') for name in fuel_totals.index],
            title='Total Generation Distribution'
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Motion chart - Time series animation
    st.markdown("### 🎬 Motion Chart - Generation Evolution")
    
    # Prepare data for motion chart
    motion_data = []
    
    # Sample data points for smoother animation (every 24 hours)
    sample_data = filtered_data.iloc[::24].copy() if len(filtered_data) > 100 else filtered_data.copy()
    
    for _, row in sample_data.iterrows():
        for fuel in selected_fuels:
            motion_data.append({
                'timestamp': row['timestamp'],
                'fuel_type': fuel.replace('_', ' '),
                'generation': row[fuel],
                'total_generation': row['Total_Generation'],
                'percentage': (row[fuel] / row['Total_Generation'] * 100) if row['Total_Generation'] > 0 else 0
            })
    
    motion_df = pd.DataFrame(motion_data)
    
    if len(motion_df) > 0:
        fig_motion = px.scatter(
            motion_df,
            x='generation',
            y='percentage',
            size='generation',
            color='fuel_type',
            animation_frame='timestamp',
            title='Fuel Generation vs Percentage Share (Motion Chart)',
            labels={
                'generation': 'Generation (MW)',
                'percentage': 'Percentage of Total (%)',
                'fuel_type': 'Fuel Type'
            }
        )
        fig_motion.update_layout(height=500)
        st.plotly_chart(fig_motion, use_container_width=True)
    
    # Daily and hourly patterns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⏰ Generation by Hour")
        hourly_gen = filtered_data.groupby('Hour')[selected_fuels].mean()
        
        fig_hourly = go.Figure()
        for fuel in selected_fuels:
            fig_hourly.add_trace(go.Scatter(
                x=hourly_gen.index,
                y=hourly_gen[fuel],
                mode='lines+markers',
                name=fuel.replace('_', ' ')
            ))
        
        fig_hourly.update_layout(
            title='Average Generation by Hour of Day',
            xaxis_title='Hour',
            yaxis_title='Generation (MW)',
            height=400
        )
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    with col2:
        st.markdown("### 📅 Generation by Day of Week")
        daily_gen = filtered_data.groupby('Day_of_Week')[selected_fuels].mean()
        
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_gen = daily_gen.reindex(day_order)
        
        # Create stacked bar chart
        fig_daily = go.Figure()
        for fuel in selected_fuels:
            fig_daily.add_trace(go.Bar(
                name=fuel.replace('_', ' '),
                x=daily_gen.index,
                y=daily_gen[fuel]
            ))
        
        fig_daily.update_layout(
            title='Average Generation by Day of Week',
            xaxis_title='Day of Week',
            yaxis_title='Generation (MW)',
            barmode='stack',
            height=400
        )
        st.plotly_chart(fig_daily, use_container_width=True)
    
    # Interactive data table
    st.markdown("### 📋 Interactive Generation Data Table")
    
    # Table options
    col1, col2, col3 = st.columns(3)
    with col1:
        table_rows = st.selectbox("Rows to display", [50, 100, 500, 1000], index=1)
    with col2:
        sort_column = st.selectbox("Sort by", ['timestamp', 'Total_Generation'] + selected_fuels)
    with col3:
        sort_order = st.selectbox("Sort order", ['Ascending', 'Descending'])
    
    # Prepare table data
    table_columns = ['timestamp', 'Total_Generation'] + selected_fuels
    table_data = filtered_data[table_columns].copy()
    
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
        if st.button("📊 Download Generation Mix Data (CSV)"):
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"ontario_genmix_{date_range[0] if len(date_range)==2 else 'latest'}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📈 Download Fuel Summary"):
            fuel_summary = filtered_data[selected_fuels].describe()
            csv_summary = fuel_summary.to_csv()
            st.download_button(
                label="Download Summary",
                data=csv_summary,
                file_name=f"genmix_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # Data info
    st.markdown("---")
    st.markdown(f"**Data Summary:** Showing {len(filtered_data):,} records with {len(selected_fuels)} fuel types from {filtered_data['timestamp'].min()} to {filtered_data['timestamp'].max()}") 