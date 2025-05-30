import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from utils.data_loader import load_energy_lmp_data, refresh_cache

def show():
    """Energy LMP (Locational Marginal Pricing) Analysis - Big Data Analytics"""
    
    st.markdown('<h1 class="page-header">⚡ Energy LMP Analysis</h1>', unsafe_allow_html=True)
    st.markdown("**Large-scale energy pricing analytics and market insights**")
    
    try:
        # Load data
        with st.spinner("Loading Energy LMP data from Azure..."):
            lmp_data = load_energy_lmp_data()
        
        if lmp_data is None:
            st.error("❌ Unable to load Energy LMP data. Please check your Azure connection.")
            return
        
        st.success(f"✅ Big Data loaded successfully! Shape: {lmp_data.shape}")
        
        # Display data info
        st.write("**Columns in dataset:**", list(lmp_data.columns))
        
        # Data preprocessing
        if 'timestamp' in lmp_data.columns:
            lmp_data['timestamp'] = pd.to_datetime(lmp_data['timestamp'])
            lmp_data['Date'] = lmp_data['timestamp'].dt.date
            lmp_data['Hour'] = lmp_data['timestamp'].dt.hour
            lmp_data['Day_of_Week'] = lmp_data['timestamp'].dt.day_name()
            lmp_data['Month'] = lmp_data['timestamp'].dt.month_name()
            lmp_data['Quarter'] = lmp_data['timestamp'].dt.quarter
            lmp_data['Year'] = lmp_data['timestamp'].dt.year
        
        # Get numeric columns for price analysis
        numeric_cols = lmp_data.select_dtypes(include=[np.number]).columns.tolist()
        
        # Sidebar filters
        st.sidebar.markdown("### 🎛️ Big Data Filters")
        
        if 'timestamp' in lmp_data.columns:
            # Advanced date filtering
            min_date = lmp_data['Date'].min()
            max_date = lmp_data['Date'].max()
            
            date_range = st.sidebar.date_input(
                "Select Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            # Time-based filters
            col1, col2 = st.sidebar.columns(2)
            with col1:
                selected_months = st.multiselect(
                    "Months",
                    options=sorted(lmp_data['Month'].unique()),
                    default=sorted(lmp_data['Month'].unique())
                )
            
            with col2:
                selected_quarters = st.multiselect(
                    "Quarters",
                    options=sorted(lmp_data['Quarter'].unique()),
                    default=sorted(lmp_data['Quarter'].unique())
                )
            
            # Hour and day filters
            hours = st.sidebar.multiselect(
                "Select Hours (0-23)",
                options=list(range(24)),
                default=list(range(24))
            )
            
            days_of_week = st.sidebar.multiselect(
                "Days of Week",
                options=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                default=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            )
            
            # Apply filters
            if len(date_range) == 2:
                filtered_data = lmp_data[
                    (lmp_data['Date'] >= date_range[0]) &
                    (lmp_data['Date'] <= date_range[1]) &
                    (lmp_data['Hour'].isin(hours)) &
                    (lmp_data['Month'].isin(selected_months)) &
                    (lmp_data['Quarter'].isin(selected_quarters)) &
                    (lmp_data['Day_of_Week'].isin(days_of_week))
                ]
            else:
                filtered_data = lmp_data[
                    (lmp_data['Hour'].isin(hours)) &
                    (lmp_data['Month'].isin(selected_months)) &
                    (lmp_data['Quarter'].isin(selected_quarters)) &
                    (lmp_data['Day_of_Week'].isin(days_of_week))
                ]
        else:
            filtered_data = lmp_data
        
        # Sampling for large datasets
        data_size = len(filtered_data)
        if data_size > 100000:
            sample_size = st.sidebar.slider(
                "Sample size for visualization (large dataset detected)",
                min_value=10000,
                max_value=min(500000, data_size),
                value=50000,
                step=10000
            )
            viz_data = filtered_data.sample(n=sample_size, random_state=42)
            st.info(f"📊 Using {sample_size:,} sample from {data_size:,} total records for visualizations")
        else:
            viz_data = filtered_data
        
        # Refresh button
        if st.sidebar.button("🔄 Refresh Data"):
            refresh_cache()
            st.experimental_rerun()
        
        # Big Data Summary metrics
        st.markdown("### 📊 Big Data Insights")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if numeric_cols:
                avg_price = filtered_data[numeric_cols].mean().mean()
                st.metric("Avg LMP", f"${avg_price:.2f}" if pd.notna(avg_price) else "N/A")
        
        with col2:
            if numeric_cols:
                max_price = filtered_data[numeric_cols].max().max()
                st.metric("Peak LMP", f"${max_price:.2f}" if pd.notna(max_price) else "N/A")
        
        with col3:
            if numeric_cols:
                price_volatility = filtered_data[numeric_cols].std().mean()
                st.metric("Volatility", f"${price_volatility:.2f}" if pd.notna(price_volatility) else "N/A")
        
        with col4:
            data_span_days = (filtered_data['timestamp'].max() - filtered_data['timestamp'].min()).days if 'timestamp' in filtered_data.columns else 0
            st.metric("Data Span", f"{data_span_days} days")
        
        # Advanced Analytics
        if 'timestamp' in lmp_data.columns and numeric_cols:
            st.markdown("### 🔬 Advanced LMP Analytics")
            
            # Clean time series chart
            st.markdown("#### Price Trends Over Time")
            
            fig_clean = go.Figure()
            colors = px.colors.qualitative.Set3
            
            # Show only top 3 locations for clarity
            for i, col in enumerate(numeric_cols[:3]):
                fig_clean.add_trace(go.Scatter(
                    x=viz_data['timestamp'],
                    y=viz_data[col],
                    mode='lines',
                    name=col,
                    line=dict(color=colors[i % len(colors)], width=2)
                ))
            
            fig_clean.update_layout(
                title='LMP Prices - Top 3 Locations',
                xaxis_title='Date & Time',
                yaxis_title='Price ($)',
                height=400,
                hovermode='x unified',
                showlegend=True
            )
            st.plotly_chart(fig_clean, use_container_width=True)
            
            # Market analysis
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Market Heat Map")
                if len(numeric_cols) > 1:
                    # Create hourly price heatmap
                    hourly_prices = filtered_data.groupby('Hour')[numeric_cols].mean()
                    
                    fig_heatmap = px.imshow(
                        hourly_prices.T,
                        x=hourly_prices.index,
                        y=hourly_prices.columns,
                        color_continuous_scale='RdYlBu_r',
                        title='Average LMP by Hour and Location',
                        aspect='auto'
                    )
                    fig_heatmap.update_layout(height=400)
                    fig_heatmap.update_xaxes(title="Hour of Day")
                    fig_heatmap.update_yaxes(title="Location")
                    st.plotly_chart(fig_heatmap, use_container_width=True)
            
            with col2:
                st.markdown("#### Price Distribution Analysis")
                if len(numeric_cols) > 0:
                    # Violin plot for price distributions
                    price_data = filtered_data[numeric_cols[:8]].melt(var_name='Location', value_name='Price')
                    
                    fig_violin = px.violin(
                        price_data,
                        x='Location',
                        y='Price',
                        title='Price Distribution by Location',
                        box=True
                    )
                    fig_violin.update_xaxes(tickangle=45)
                    fig_violin.update_layout(height=400)
                    st.plotly_chart(fig_violin, use_container_width=True)
            
            # Time-based analytics
            st.markdown("#### Temporal Analytics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("##### Monthly Trends")
                monthly_avg = filtered_data.groupby('Month')[numeric_cols].mean().mean(axis=1)
                fig_monthly = px.bar(
                    x=monthly_avg.index,
                    y=monthly_avg.values,
                    title='Average LMP by Month'
                )
                fig_monthly.update_layout(height=300)
                st.plotly_chart(fig_monthly, use_container_width=True)
            
            with col2:
                st.markdown("##### Quarterly Analysis")
                quarterly_avg = filtered_data.groupby('Quarter')[numeric_cols].mean().mean(axis=1)
                fig_quarterly = px.pie(
                    values=quarterly_avg.values,
                    names=[f'Q{q}' for q in quarterly_avg.index],
                    title='LMP Distribution by Quarter'
                )
                fig_quarterly.update_layout(height=300)
                st.plotly_chart(fig_quarterly, use_container_width=True)
            
            with col3:
                st.markdown("##### Day-of-Week Patterns")
                dow_avg = filtered_data.groupby('Day_of_Week')[numeric_cols].mean().mean(axis=1)
                # Reorder to start with Monday
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                dow_avg = dow_avg.reindex([day for day in day_order if day in dow_avg.index])
                
                fig_dow = px.line(
                    x=dow_avg.index,
                    y=dow_avg.values,
                    title='Average LMP by Day of Week',
                    markers=True
                )
                fig_dow.update_layout(height=300)
                fig_dow.update_xaxes(tickangle=45)
                st.plotly_chart(fig_dow, use_container_width=True)
        
        # Big Data Table Explorer
        st.markdown("### 📋 Big Data Explorer")
        
        # Advanced table options
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            table_rows = st.selectbox("Rows to display", [100, 500, 1000, 5000, 10000], index=2)
        with col2:
            available_columns = filtered_data.columns.tolist()
            sort_column = st.selectbox("Sort by", available_columns)
        with col3:
            sort_order = st.selectbox("Sort order", ['Ascending', 'Descending'])
        with col4:
            show_stats = st.checkbox("Show column statistics", value=True)
        
        # Sort and display data
        ascending = sort_order == 'Ascending'
        display_data = filtered_data.sort_values(sort_column, ascending=ascending)
        
        st.dataframe(
            display_data.head(table_rows),
            use_container_width=True,
            height=500
        )
        
        # Statistical analysis
        if show_stats and numeric_cols:
            st.markdown("### 📊 Statistical Analysis")
            
            # Comprehensive statistics
            stats_df = filtered_data[numeric_cols].describe()
            
            # Add additional statistics
            stats_df.loc['variance'] = filtered_data[numeric_cols].var()
            stats_df.loc['skewness'] = filtered_data[numeric_cols].skew()
            stats_df.loc['kurtosis'] = filtered_data[numeric_cols].kurtosis()
            
            st.dataframe(stats_df, use_container_width=True)
        
        # Download options for big data
        st.markdown("### 💾 Export Big Data")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Download Filtered Data (CSV)"):
                csv = filtered_data.to_csv(index=False)
                filename = f"energy_lmp_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                st.download_button(
                    label="Download Full Dataset",
                    data=csv,
                    file_name=filename,
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📈 Download Analytics Summary"):
                if numeric_cols:
                    summary = filtered_data[numeric_cols].describe()
                    csv_summary = summary.to_csv()
                    st.download_button(
                        label="Download Analytics",
                        data=csv_summary,
                        file_name=f"energy_lmp_analytics_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
        
        with col3:
            if st.button("🔬 Download Sample Data"):
                sample_data = filtered_data.sample(n=min(10000, len(filtered_data)), random_state=42)
                csv_sample = sample_data.to_csv(index=False)
                st.download_button(
                    label="Download Sample (10k records)",
                    data=csv_sample,
                    file_name=f"energy_lmp_sample_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        # Big Data summary
        st.markdown("---")
        if 'timestamp' in filtered_data.columns:
            min_timestamp = filtered_data['timestamp'].min()
            max_timestamp = filtered_data['timestamp'].max()
            total_hours = (max_timestamp - min_timestamp).total_seconds() / 3600
            st.markdown(f"**Big Data Summary:** {len(filtered_data):,} records spanning {total_hours:.0f} hours from {min_timestamp.strftime('%Y-%m-%d %H:%M')} to {max_timestamp.strftime('%Y-%m-%d %H:%M')}")
            st.markdown(f"**Data Volume:** ~{len(filtered_data) * len(filtered_data.columns) / 1000000:.1f}M data points analyzed")
        else:
            st.markdown(f"**Big Data Summary:** {len(filtered_data):,} records loaded for analysis")
        
    except Exception as e:
        st.error(f"❌ Error in Energy LMP big data analysis: {str(e)}")
        import traceback
        st.text("Full error traceback:")
        st.text(traceback.format_exc()) 