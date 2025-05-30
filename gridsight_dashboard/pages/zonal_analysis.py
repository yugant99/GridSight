import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from utils.data_loader import load_zonal_data, refresh_cache

def show():
    """Zonal Analysis page with regional demand patterns"""
    
    st.markdown('<h1 class="page-header">🗺️ Ontario Zonal Demand Analysis</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading zonal demand data from Azure..."):
        zonal_data = load_zonal_data()
    
    if zonal_data is None:
        st.warning("⚠️ Zonal data not available. This may be due to:")
        st.info("• Limited data collection period")
        st.info("• Data not yet processed")
        st.info("• Different file naming convention")
        
        # Show mock zonal analysis as demonstration
        st.markdown("### 📊 Zonal Analysis Demo")
        st.info("Below is a demonstration of what zonal analysis would look like when data becomes available:")
        
        # Create demo data
        demo_zones = ['Toronto', 'Ottawa', 'Northwest', 'Northeast', 'Southwest', 'Niagara', 'Bruce']
        demo_data = []
        
        # Generate sample data for demonstration
        base_date = datetime.now() - timedelta(days=30)
        for i in range(720):  # 30 days of hourly data
            timestamp = base_date + timedelta(hours=i)
            for zone in demo_zones:
                # Create realistic-looking demand patterns
                hour = timestamp.hour
                day_of_week = timestamp.weekday()
                
                # Base demand varies by zone
                zone_multipliers = {
                    'Toronto': 3.5, 'Ottawa': 1.2, 'Northwest': 0.3, 
                    'Northeast': 0.4, 'Southwest': 1.8, 'Niagara': 0.7, 'Bruce': 0.5
                }
                
                base_demand = zone_multipliers[zone] * 1000
                
                # Add hourly and weekly patterns
                hourly_factor = 0.8 + 0.4 * np.sin(2 * np.pi * (hour - 6) / 24)
                weekend_factor = 0.9 if day_of_week >= 5 else 1.0
                
                # Add some randomness
                random_factor = np.random.normal(1.0, 0.1)
                
                demand = base_demand * hourly_factor * weekend_factor * random_factor
                
                demo_data.append({
                    'timestamp': timestamp,
                    'zone': zone,
                    'demand': max(0, demand)
                })
        
        demo_df = pd.DataFrame(demo_data)
        
        # Demo visualizations
        st.markdown("#### 🏙️ Average Demand by Zone")
        zone_avg = demo_df.groupby('zone')['demand'].mean().sort_values(ascending=True)
        
        fig_zones = px.bar(
            x=zone_avg.values,
            y=zone_avg.index,
            orientation='h',
            title='Average Demand by Zone (Demo Data)',
            color=zone_avg.values,
            color_continuous_scale='viridis'
        )
        fig_zones.update_layout(height=400)
        fig_zones.update_layout(xaxis_title="Average Demand (MW)", yaxis_title="Zone")
        st.plotly_chart(fig_zones, use_container_width=True)
        
        # Time series by zone
        st.markdown("#### 📈 Demand Trends by Zone")
        
        # Sample recent data for cleaner visualization
        recent_data = demo_df[demo_df['timestamp'] >= demo_df['timestamp'].max() - timedelta(days=7)]
        
        fig_ts_zones = px.line(
            recent_data,
            x='timestamp',
            y='demand',
            color='zone',
            title='7-Day Demand Trends by Zone (Demo Data)',
            labels={'demand': 'Demand (MW)', 'timestamp': 'Date & Time'}
        )
        fig_ts_zones.update_layout(height=500)
        st.plotly_chart(fig_ts_zones, use_container_width=True)
        
        # Heatmap
        st.markdown("#### 🔥 Zone Demand Heatmap")
        
        # Create hourly heatmap data
        demo_df['hour'] = demo_df['timestamp'].dt.hour
        demo_df['date'] = demo_df['timestamp'].dt.date
        
        # Get recent week for heatmap
        recent_week = demo_df[demo_df['timestamp'] >= demo_df['timestamp'].max() - timedelta(days=7)]
        heatmap_data = recent_week.groupby(['zone', 'hour'])['demand'].mean().reset_index()
        heatmap_pivot = heatmap_data.pivot(index='zone', columns='hour', values='demand')
        
        fig_heatmap = px.imshow(
            heatmap_pivot,
            title='Average Hourly Demand by Zone (Demo Data)',
            labels=dict(x="Hour of Day", y="Zone", color="Demand (MW)"),
            aspect="auto",
            color_continuous_scale='Viridis'
        )
        fig_heatmap.update_layout(height=400)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        return
    
    # Real zonal data processing (when available)
    # Data preprocessing
    zonal_data['timestamp'] = pd.to_datetime(zonal_data['timestamp'])
    zonal_data['Date'] = zonal_data['timestamp'].dt.date
    zonal_data['Hour'] = zonal_data['timestamp'].dt.hour
    zonal_data['Day_of_Week'] = zonal_data['timestamp'].dt.day_name()
    zonal_data['Month'] = zonal_data['timestamp'].dt.month_name()
    
    # Get zone columns (excluding timestamp and derived columns)
    zone_columns = [col for col in zonal_data.columns if col not in ['timestamp', 'Date', 'Hour', 'Day_of_Week', 'Month']]
    
    # Sidebar filters
    st.sidebar.markdown("### 🎛️ Data Filters")
    
    # Date range filter
    min_date = zonal_data['Date'].min()
    max_date = zonal_data['Date'].max()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Zone filter
    selected_zones = st.sidebar.multiselect(
        "Select Zones",
        options=zone_columns,
        default=zone_columns
    )
    
    # Hour filter
    hours = st.sidebar.multiselect(
        "Select Hours (0-23)",
        options=list(range(24)),
        default=list(range(24))
    )
    
    # Apply filters
    if len(date_range) == 2:
        filtered_data = zonal_data[
            (zonal_data['Date'] >= date_range[0]) &
            (zonal_data['Date'] <= date_range[1]) &
            (zonal_data['Hour'].isin(hours))
        ]
    else:
        filtered_data = zonal_data[zonal_data['Hour'].isin(hours)]
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        refresh_cache()
        st.experimental_rerun()
    
    # Calculate totals
    filtered_data['Total_Zonal_Demand'] = filtered_data[selected_zones].sum(axis=1)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_demand = filtered_data['Total_Zonal_Demand'].mean()
        st.metric("Avg Total Demand", f"{total_demand:,.0f} MW")
    
    with col2:
        max_demand = filtered_data['Total_Zonal_Demand'].max()
        st.metric("Peak Demand", f"{max_demand:,.0f} MW")
    
    with col3:
        # Most demanding zone
        zone_avg = filtered_data[selected_zones].mean()
        dominant_zone = zone_avg.idxmax()
        st.metric("Highest Demand Zone", dominant_zone)
    
    with col4:
        # Zone count
        st.metric("Active Zones", len(selected_zones))
    
    # Main visualizations
    st.markdown("### 🏙️ Zonal Demand Distribution")
    
    # Zone comparison bar chart
    zone_avg = filtered_data[selected_zones].mean().sort_values(ascending=True)
    
    fig_zones = px.bar(
        x=zone_avg.values,
        y=zone_avg.index,
        orientation='h',
        title='Average Demand by Zone',
        color=zone_avg.values,
        color_continuous_scale='viridis'
    )
    fig_zones.update_layout(height=400, showlegend=False)
    fig_zones.update_layout(xaxis_title="Average Demand (MW)", yaxis_title="Zone")
    st.plotly_chart(fig_zones, use_container_width=True)
    
    # Time series analysis
    st.markdown("### 📈 Zonal Demand Trends")
    
    # Line chart for all zones
    melted_data = filtered_data.melt(
        id_vars=['timestamp'], 
        value_vars=selected_zones,
        var_name='Zone',
        value_name='Demand'
    )
    
    fig_ts_zones = px.line(
        melted_data,
        x='timestamp',
        y='Demand',
        color='Zone',
        title='Demand Trends by Zone',
        labels={'Demand': 'Demand (MW)', 'timestamp': 'Date & Time'}
    )
    fig_ts_zones.update_layout(height=500)
    st.plotly_chart(fig_ts_zones, use_container_width=True)
    
    # Comparative analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🥧 Zone Demand Distribution")
        zone_totals = filtered_data[selected_zones].sum()
        
        fig_pie = px.pie(
            values=zone_totals.values,
            names=zone_totals.index,
            title='Total Demand Distribution by Zone'
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Zone Peak vs Average")
        zone_stats = pd.DataFrame({
            'Zone': selected_zones,
            'Average': [filtered_data[zone].mean() for zone in selected_zones],
            'Peak': [filtered_data[zone].max() for zone in selected_zones]
        })
        
        fig_comparison = go.Figure()
        fig_comparison.add_trace(go.Bar(
            name='Average',
            x=zone_stats['Zone'],
            y=zone_stats['Average']
        ))
        fig_comparison.add_trace(go.Bar(
            name='Peak',
            x=zone_stats['Zone'],
            y=zone_stats['Peak']
        ))
        
        fig_comparison.update_layout(
            title='Peak vs Average Demand by Zone',
            xaxis_title='Zone',
            yaxis_title='Demand (MW)',
            barmode='group',
            height=400
        )
        st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Heatmap analysis
    st.markdown("### 🔥 Hourly Demand Heatmap by Zone")
    
    # Create hourly heatmap data
    heatmap_data = filtered_data.groupby('Hour')[selected_zones].mean()
    
    fig_heatmap = px.imshow(
        heatmap_data.T,
        title='Average Hourly Demand by Zone',
        labels=dict(x="Hour of Day", y="Zone", color="Demand (MW)"),
        aspect="auto",
        color_continuous_scale='Viridis'
    )
    fig_heatmap.update_layout(height=500)
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Interactive data table
    st.markdown("### 📋 Interactive Zonal Data Table")
    
    # Table options
    col1, col2, col3 = st.columns(3)
    with col1:
        table_rows = st.selectbox("Rows to display", [50, 100, 500, 1000], index=1)
    with col2:
        sort_column = st.selectbox("Sort by", ['timestamp', 'Total_Zonal_Demand'] + selected_zones)
    with col3:
        sort_order = st.selectbox("Sort order", ['Ascending', 'Descending'])
    
    # Prepare table data
    table_columns = ['timestamp', 'Total_Zonal_Demand'] + selected_zones
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
        if st.button("📊 Download Zonal Data (CSV)"):
            csv = filtered_data.to_csv(index=False)
            # Fix filename generation to handle date types properly
            if len(date_range) == 2:
                filename = f"ontario_zonal_{str(date_range[0])}_{str(date_range[1])}.csv"
            else:
                filename = f"ontario_zonal_latest_{datetime.now().strftime('%Y%m%d')}.csv"
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=filename,
                mime="text/csv"
            )
    
    with col2:
        if st.button("📈 Download Zone Summary"):
            zone_summary = filtered_data[selected_zones].describe()
            csv_summary = zone_summary.to_csv()
            st.download_button(
                label="Download Summary",
                data=csv_summary,
                file_name=f"zonal_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # Data info
    st.markdown("---")
    st.markdown(f"**Data Summary:** Showing {len(filtered_data):,} records across {len(selected_zones)} zones from {filtered_data['timestamp'].min()} to {filtered_data['timestamp'].max()}") 