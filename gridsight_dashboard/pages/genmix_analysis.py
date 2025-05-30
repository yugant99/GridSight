import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from utils.data_loader import load_genmix_data, refresh_cache

def show():
    """Ontario Generation Mix Analysis with interactive visualizations"""
    
    st.markdown('<h1 class="page-header">⚡ Ontario Generation Mix Analysis</h1>', unsafe_allow_html=True)
    
    try:
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
        
        # Get unique fuel types
        fuel_types = sorted(genmix_data['fuel'].unique())
        
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
            options=fuel_types,
            default=fuel_types
        )
        
        # Hour filter
        hours = st.sidebar.multiselect(
            "Select Hours (0-23)",
            options=list(range(24)),
            default=list(range(24))
        )
        
        # Quality filter
        quality_levels = sorted(genmix_data['output_quality'].unique())
        selected_quality = st.sidebar.multiselect(
            "Select Output Quality",
            options=quality_levels,
            default=quality_levels
        )
        
        # Apply filters
        filtered_data = genmix_data[
            (genmix_data['Date'] >= date_range[0]) &
            (genmix_data['Date'] <= date_range[1]) &
            (genmix_data['Hour'].isin(hours)) &
            (genmix_data['fuel'].isin(selected_fuels)) &
            (genmix_data['output_quality'].isin(selected_quality))
        ]
        
        # Refresh button
        if st.sidebar.button("🔄 Refresh Data"):
            refresh_cache()
            st.experimental_rerun()
        
        # Summary metrics
        st.markdown("### 📊 Key Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_output = filtered_data['output'].mean()
            avg_output_display = f"{avg_output:,.0f} MW" if pd.notna(avg_output) else "N/A"
            st.metric("Avg Output", avg_output_display)
        
        with col2:
            max_output = filtered_data['output'].max()
            max_output_display = f"{max_output:,.0f} MW" if pd.notna(max_output) else "N/A"
            st.metric("Peak Output", max_output_display)
        
        with col3:
            unique_fuels = filtered_data['fuel'].nunique()
            st.metric("Fuel Types", unique_fuels)
        
        # Main visualizations
        st.markdown("### 📈 Generation Mix Visualizations")
        
        # Time series chart
        st.markdown("#### Generation Output Over Time")
        
        # Pivot data for time series
        pivot_data = filtered_data.pivot_table(
            index='timestamp',
            columns='fuel',
            values='output',
            aggfunc='sum'
        ).fillna(0)
        
        if not pivot_data.empty:
            fig_time = go.Figure()
            
            colors = px.colors.qualitative.Set3
            for i, fuel in enumerate(pivot_data.columns):
                fig_time.add_trace(go.Scatter(
                    x=pivot_data.index,
                    y=pivot_data[fuel],
                    mode='lines',
                    name=fuel,
                    line=dict(color=colors[i % len(colors)])
                ))
            
            fig_time.update_layout(
                title='Generation Output by Fuel Type Over Time',
                xaxis_title='Date & Time',
                yaxis_title='Output (MW)',
                height=500,
                hovermode='x unified'
            )
            st.plotly_chart(fig_time, use_container_width=True)
        
        # Fuel comparison charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Average Output by Fuel Type")
            fuel_avg = filtered_data.groupby('fuel')['output'].mean().sort_values(ascending=True)
            
            fig_bar = px.bar(
                x=fuel_avg.values,
                y=fuel_avg.index,
                orientation='h',
                title='Average Output by Fuel Type',
                color=fuel_avg.values,
                color_continuous_scale='viridis',
                labels={'x': 'Average Output (MW)', 'y': 'Fuel Type'}
            )
            fig_bar.update_layout(
                height=400, 
                showlegend=False,
                xaxis_title="Average Output (MW)",
                yaxis_title="Fuel Type"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            st.markdown("#### Total Output Distribution")
            fuel_totals = filtered_data.groupby('fuel')['output'].sum()
            
            fig_pie = px.pie(
                values=fuel_totals.values,
                names=fuel_totals.index,
                title='Total Output Distribution'
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Hourly and daily patterns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Generation Patterns by Hour")
            hourly_data = filtered_data.groupby(['Hour', 'fuel'])['output'].mean().unstack(fill_value=0)
            
            fig_hourly = go.Figure()
            for fuel in hourly_data.columns:
                fig_hourly.add_trace(go.Scatter(
                    x=hourly_data.index,
                    y=hourly_data[fuel],
                    mode='lines+markers',
                    name=fuel
                ))
            
            fig_hourly.update_layout(
                title='Average Generation by Hour of Day',
                xaxis_title='Hour',
                yaxis_title='Output (MW)',
                height=400
            )
            st.plotly_chart(fig_hourly, use_container_width=True)
        
        with col2:
            st.markdown("#### Generation by Day of Week")
            daily_data = filtered_data.groupby(['Day_of_Week', 'fuel'])['output'].mean().unstack(fill_value=0)
            
            # Reorder days
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            daily_data = daily_data.reindex(day_order)
            
            fig_daily = go.Figure()
            for fuel in daily_data.columns:
                fig_daily.add_trace(go.Bar(
                    name=fuel,
                    x=daily_data.index,
                    y=daily_data[fuel]
                ))
            
            fig_daily.update_layout(
                title='Average Generation by Day of Week',
                xaxis_title='Day of Week',
                yaxis_title='Output (MW)',
                barmode='stack',
                height=400
            )
            st.plotly_chart(fig_daily, use_container_width=True)
        
        # Data quality analysis
        st.markdown("#### Data Quality Analysis")
        quality_summary = filtered_data.groupby(['fuel', 'output_quality']).size().unstack(fill_value=0)
        
        fig_quality = px.imshow(
            quality_summary.values,
            x=quality_summary.columns,
            y=quality_summary.index,
            color_continuous_scale='Blues',
            title='Data Quality Distribution by Fuel Type'
        )
        fig_quality.update_layout(height=400)
        st.plotly_chart(fig_quality, use_container_width=True)
        
        # Interactive data table
        st.markdown("### 📋 Generation Data Explorer")
        
        # Table options
        col1, col2, col3 = st.columns(3)
        with col1:
            table_rows = st.selectbox("Rows to display", [100, 500, 1000, 5000], index=1)
        with col2:
            sort_column = st.selectbox("Sort by", ['timestamp', 'fuel', 'output', 'output_quality'])
        with col3:
            sort_order = st.selectbox("Sort order", ['Ascending', 'Descending'])
        
        # Sort and display data
        ascending = sort_order == 'Ascending'
        display_data = filtered_data.sort_values(sort_column, ascending=ascending)
        
        st.dataframe(
            display_data.head(table_rows),
            use_container_width=True,
            height=400
        )
        
        # Download options
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Download Filtered Data (CSV)"):
                csv = filtered_data.to_csv(index=False)
                filename = f"ontario_genmix_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=filename,
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📈 Download Summary Statistics"):
                summary = filtered_data.groupby('fuel')['output'].describe()
                csv_summary = summary.to_csv()
                st.download_button(
                    label="Download Summary",
                    data=csv_summary,
                    file_name=f"genmix_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        # Data summary
        st.markdown("---")
        min_timestamp = filtered_data['timestamp'].min()
        max_timestamp = filtered_data['timestamp'].max()
        st.markdown(f"**Data Summary:** {len(filtered_data):,} records from {len(selected_fuels)} fuel types, spanning {min_timestamp.strftime('%Y-%m-%d %H:%M')} to {max_timestamp.strftime('%Y-%m-%d %H:%M')}")
        
    except Exception as e:
        st.error(f"❌ Error in generation mix analysis: {str(e)}")
        import traceback
        st.text("Full error traceback:")
        st.text(traceback.format_exc()) 