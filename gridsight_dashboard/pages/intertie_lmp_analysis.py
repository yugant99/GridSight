import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from utils.data_loader import load_intertie_lmp_data, refresh_cache

def show():
    """Intertie LMP (Locational Marginal Pricing) Analysis"""
    
    st.markdown('<h1 class="page-header">🔗 Intertie LMP Analysis</h1>', unsafe_allow_html=True)
    
    try:
        # Load data
        with st.spinner("Loading Intertie LMP data from Azure..."):
            lmp_data = load_intertie_lmp_data()
        
        if lmp_data is None:
            st.error("❌ Unable to load Intertie LMP data. Please check your Azure connection.")
            return
        
        st.success(f"✅ Data loaded successfully! Shape: {lmp_data.shape}")
        
        # Display data info
        st.write("**Columns in dataset:**", list(lmp_data.columns))
        
        # Data preprocessing
        if 'timestamp' in lmp_data.columns:
            lmp_data['timestamp'] = pd.to_datetime(lmp_data['timestamp'])
            lmp_data['Date'] = lmp_data['timestamp'].dt.date
            lmp_data['Hour'] = lmp_data['timestamp'].dt.hour
            lmp_data['Day_of_Week'] = lmp_data['timestamp'].dt.day_name()
            lmp_data['Month'] = lmp_data['timestamp'].dt.month_name()
        
        # Get numeric columns for price analysis
        numeric_cols = lmp_data.select_dtypes(include=[np.number]).columns.tolist()
        
        # Sidebar filters
        st.sidebar.markdown("### 🎛️ Data Filters")
        
        if 'timestamp' in lmp_data.columns:
            # Date range filter
            min_date = lmp_data['Date'].min()
            max_date = lmp_data['Date'].max()
            
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
            
            # Apply filters
            if len(date_range) == 2:
                filtered_data = lmp_data[
                    (lmp_data['Date'] >= date_range[0]) &
                    (lmp_data['Date'] <= date_range[1]) &
                    (lmp_data['Hour'].isin(hours))
                ]
            else:
                filtered_data = lmp_data[lmp_data['Hour'].isin(hours)]
        else:
            filtered_data = lmp_data
        
        # Refresh button
        if st.sidebar.button("🔄 Refresh Data"):
            refresh_cache()
            st.experimental_rerun()
        
        # Summary metrics
        st.markdown("### 📊 Key Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if numeric_cols:
                avg_price = filtered_data[numeric_cols].mean().mean()
                st.metric("Avg Price", f"${avg_price:.2f}" if pd.notna(avg_price) else "N/A")
        
        with col2:
            if numeric_cols:
                max_price = filtered_data[numeric_cols].max().max()
                st.metric("Peak Price", f"${max_price:.2f}" if pd.notna(max_price) else "N/A")
        
        with col3:
            if numeric_cols:
                price_volatility = filtered_data[numeric_cols].std().mean()
                st.metric("Price Volatility", f"${price_volatility:.2f}" if pd.notna(price_volatility) else "N/A")
        
        # Main visualizations
        if 'timestamp' in lmp_data.columns and numeric_cols:
            st.markdown("### 📈 LMP Visualizations")
            
            # Time series chart
            st.markdown("#### LMP Prices Over Time")
            
            fig_time = go.Figure()
            colors = px.colors.qualitative.Set3
            
            for i, col in enumerate(numeric_cols[:10]):  # Limit to first 10 for readability
                fig_time.add_trace(go.Scatter(
                    x=filtered_data['timestamp'],
                    y=filtered_data[col],
                    mode='lines',
                    name=col,
                    line=dict(color=colors[i % len(colors)])
                ))
            
            fig_time.update_layout(
                title='Intertie LMP Prices Over Time',
                xaxis_title='Date & Time',
                yaxis_title='Price ($)',
                height=500,
                hovermode='x unified'
            )
            st.plotly_chart(fig_time, use_container_width=True)
            
            # Price distribution and patterns
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Price Distribution")
                if len(numeric_cols) > 0:
                    price_data = filtered_data[numeric_cols].melt(var_name='Location', value_name='Price')
                    
                    fig_box = px.box(
                        price_data,
                        x='Location',
                        y='Price',
                        title='Price Distribution by Location'
                    )
                    fig_box.update_xaxes(tickangle=45)
                    fig_box.update_layout(height=400)
                    st.plotly_chart(fig_box, use_container_width=True)
            
            with col2:
                st.markdown("#### Hourly Price Patterns")
                hourly_avg = filtered_data.groupby('Hour')[numeric_cols].mean()
                
                fig_hourly = go.Figure()
                for col in numeric_cols[:5]:  # Show top 5 locations
                    fig_hourly.add_trace(go.Scatter(
                        x=hourly_avg.index,
                        y=hourly_avg[col],
                        mode='lines+markers',
                        name=col
                    ))
                
                fig_hourly.update_layout(
                    title='Average LMP by Hour of Day',
                    xaxis_title='Hour',
                    yaxis_title='Price ($)',
                    height=400
                )
                st.plotly_chart(fig_hourly, use_container_width=True)
            
            # Correlation matrix
            if len(numeric_cols) > 1:
                st.markdown("#### Price Correlation Matrix")
                correlation_matrix = filtered_data[numeric_cols].corr()
                
                fig_corr = px.imshow(
                    correlation_matrix.values,
                    x=correlation_matrix.columns,
                    y=correlation_matrix.index,
                    color_continuous_scale='RdBu',
                    title='LMP Price Correlations Between Locations'
                )
                fig_corr.update_layout(height=500)
                st.plotly_chart(fig_corr, use_container_width=True)
        
        # Interactive data table
        st.markdown("### 📋 LMP Data Explorer")
        
        # Table options
        col1, col2, col3 = st.columns(3)
        with col1:
            table_rows = st.selectbox("Rows to display", [100, 500, 1000, 5000], index=1)
        with col2:
            available_columns = filtered_data.columns.tolist()
            sort_column = st.selectbox("Sort by", available_columns)
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
        
        # Statistical summary
        st.markdown("### 📊 Statistical Summary")
        if numeric_cols:
            st.dataframe(
                filtered_data[numeric_cols].describe(),
                use_container_width=True
            )
        
        # Download options
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Download LMP Data (CSV)"):
                csv = filtered_data.to_csv(index=False)
                filename = f"intertie_lmp_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=filename,
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📈 Download Summary Statistics"):
                if numeric_cols:
                    summary = filtered_data[numeric_cols].describe()
                    csv_summary = summary.to_csv()
                    st.download_button(
                        label="Download Summary",
                        data=csv_summary,
                        file_name=f"intertie_lmp_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
        
        # Data summary
        st.markdown("---")
        if 'timestamp' in filtered_data.columns:
            min_timestamp = filtered_data['timestamp'].min()
            max_timestamp = filtered_data['timestamp'].max()
            st.markdown(f"**Data Summary:** {len(filtered_data):,} records spanning {min_timestamp.strftime('%Y-%m-%d %H:%M')} to {max_timestamp.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.markdown(f"**Data Summary:** {len(filtered_data):,} records loaded")
        
    except Exception as e:
        st.error(f"❌ Error in Intertie LMP analysis: {str(e)}")
        import traceback
        st.text("Full error traceback:")
        st.text(traceback.format_exc()) 