import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from utils.data_loader import load_latest_predictions, load_model_summary, refresh_cache

def show():
    """ML Predictions page showing live forecasts and model performance"""
    
    st.markdown('<h1 class="page-header">🤖 ML Predictions & Model Performance</h1>', unsafe_allow_html=True)
    
    # Load ML data
    col1, col2 = st.columns(2)
    
    with col1:
        with st.spinner("Loading latest predictions..."):
            predictions_data = load_latest_predictions()
    
    with col2:
        with st.spinner("Loading model performance data..."):
            model_summary = load_model_summary()
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh ML Data"):
        refresh_cache()
        st.experimental_rerun()
    
    # Model Performance Overview
    st.markdown("### 📊 Model Performance Summary")
    
    if model_summary:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            mae = model_summary.get('demand_model', {}).get('mae', 0)
            st.metric("Demand Model MAE", f"{mae:.1f} MW")
        
        with col2:
            accuracy = model_summary.get('stress_model', {}).get('accuracy', 0)
            st.metric("Stress Detection Accuracy", f"{accuracy:.1%}")
        
        with col3:
            training_date = model_summary.get('training_completed_at', 'Unknown')
            if training_date != 'Unknown':
                training_dt = datetime.fromisoformat(training_date.replace('Z', '+00:00'))
                st.metric("Last Training", training_dt.strftime('%Y-%m-%d %H:%M'))
            else:
                st.metric("Last Training", "Unknown")
        
        with col4:
            data_sources = model_summary.get('data_sources', {})
            demand_records = data_sources.get('demand_records', 0)
            st.metric("Training Records", f"{demand_records:,}")
    else:
        st.warning("⚠️ Model summary data not available. Check Azure connection.")
    
    # Live Predictions
    st.markdown("### 🔮 Live 24-Hour Demand Forecasts")
    
    if predictions_data and 'forecast_24h' in predictions_data:
        forecasts = predictions_data['forecast_24h']
        
        if forecasts:
            # Convert to DataFrame
            forecast_df = pd.DataFrame(forecasts)
            forecast_df['timestamp'] = pd.to_datetime(forecast_df['timestamp'])
            forecast_df['hour'] = forecast_df['timestamp'].dt.hour
            
            # Forecast time series
            fig_forecast = px.line(
                forecast_df,
                x='timestamp',
                y='predicted_demand',
                title='24-Hour Demand Forecast',
                labels={'predicted_demand': 'Predicted Demand (MW)', 'timestamp': 'Date & Time'}
            )
            
            # Add confidence intervals if available
            if 'confidence_lower' in forecast_df.columns and 'confidence_upper' in forecast_df.columns:
                fig_forecast.add_trace(go.Scatter(
                    x=forecast_df['timestamp'],
                    y=forecast_df['confidence_upper'],
                    mode='lines',
                    line=dict(width=0),
                    showlegend=False,
                    name='Upper Confidence'
                ))
                fig_forecast.add_trace(go.Scatter(
                    x=forecast_df['timestamp'],
                    y=forecast_df['confidence_lower'],
                    mode='lines',
                    line=dict(width=0),
                    fill='tonexty',
                    fillcolor='rgba(31, 119, 180, 0.2)',
                    showlegend=False,
                    name='Confidence Interval'
                ))
            
            fig_forecast.update_layout(height=500)
            fig_forecast.update_traces(line=dict(color='#1f77b4', width=3))
            st.plotly_chart(fig_forecast, use_container_width=True)
            
            # Grid stress alerts
            st.markdown("### ⚠️ Grid Stress Detection")
            
            stress_alerts = [f for f in forecasts if f.get('grid_stress_risk', 0) > 0.5]
            
            if stress_alerts:
                st.error(f"🚨 **{len(stress_alerts)} Grid Stress Alerts** detected in the next 24 hours!")
                
                # Show stress periods
                stress_df = pd.DataFrame(stress_alerts)
                stress_df['timestamp'] = pd.to_datetime(stress_df['timestamp'])
                
                fig_stress = px.scatter(
                    stress_df,
                    x='timestamp',
                    y='predicted_demand',
                    color='grid_stress_risk',
                    size='grid_stress_risk',
                    title='Grid Stress Risk Periods',
                    labels={'grid_stress_risk': 'Stress Risk', 'predicted_demand': 'Predicted Demand (MW)'},
                    color_continuous_scale='Reds'
                )
                fig_stress.update_layout(height=400)
                st.plotly_chart(fig_stress, use_container_width=True)
            else:
                st.success("✅ No grid stress alerts predicted for the next 24 hours")
            
            # Hourly breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### ⏰ Hourly Forecast Breakdown")
                hourly_avg = forecast_df.groupby('hour')['predicted_demand'].mean().reset_index()
                
                fig_hourly = px.bar(
                    hourly_avg,
                    x='hour',
                    y='predicted_demand',
                    title='Average Predicted Demand by Hour',
                    color='predicted_demand',
                    color_continuous_scale='viridis'
                )
                fig_hourly.update_layout(height=400)
                st.plotly_chart(fig_hourly, use_container_width=True)
            
            with col2:
                st.markdown("### 📈 Peak Demand Predictions")
                peak_hours = forecast_df.nlargest(5, 'predicted_demand')[['timestamp', 'predicted_demand', 'grid_stress_risk']]
                peak_hours['timestamp_str'] = peak_hours['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
                
                fig_peak = px.bar(
                    peak_hours,
                    x='timestamp_str',
                    y='predicted_demand',
                    title='Top 5 Peak Demand Periods',
                    color='grid_stress_risk',
                    color_continuous_scale='Reds'
                )
                fig_peak.update_layout(height=400)
                fig_peak.update_xaxes(tickangle=45)
                st.plotly_chart(fig_peak, use_container_width=True)
            
            # Prediction table
            st.markdown("### 📋 Detailed Forecast Table")
            
            # Table options
            col1, col2 = st.columns(2)
            with col1:
                table_rows = st.selectbox("Rows to display", [10, 24, 50], index=1)
            with col2:
                sort_column = st.selectbox("Sort by", ['timestamp', 'predicted_demand', 'grid_stress_risk'])
            
            # Format table data
            table_data = forecast_df.copy()
            table_data['timestamp'] = table_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
            table_data['predicted_demand'] = table_data['predicted_demand'].round(1)
            if 'grid_stress_risk' in table_data.columns:
                table_data['grid_stress_risk'] = (table_data['grid_stress_risk'] * 100).round(1)
            
            # Display table
            st.dataframe(
                table_data.head(table_rows),
                use_container_width=True,
                height=400
            )
        else:
            st.warning("⚠️ No forecast data available")
    else:
        st.error("❌ Unable to load prediction data. Check Azure ML Orchestrator status.")
    
    # Model Feature Importance
    if model_summary:
        st.markdown("### 🔍 Model Feature Importance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Demand Forecasting Model")
            demand_importance = model_summary.get('demand_model', {}).get('feature_importance', {})
            
            if demand_importance:
                importance_df = pd.DataFrame(list(demand_importance.items()), 
                                           columns=['Feature', 'Importance'])
                importance_df = importance_df.sort_values('Importance', ascending=True)
                
                fig_importance = px.bar(
                    importance_df,
                    x='Importance',
                    y='Feature',
                    orientation='h',
                    title='Feature Importance - Demand Model',
                    color='Importance',
                    color_continuous_scale='blues'
                )
                fig_importance.update_layout(height=400)
                st.plotly_chart(fig_importance, use_container_width=True)
            else:
                st.info("Feature importance data not available")
        
        with col2:
            st.markdown("#### Grid Stress Detection Model")
            stress_importance = model_summary.get('stress_model', {}).get('feature_importance', {})
            
            if stress_importance:
                stress_df = pd.DataFrame(list(stress_importance.items()), 
                                       columns=['Feature', 'Importance'])
                stress_df = stress_df.sort_values('Importance', ascending=True)
                
                fig_stress_imp = px.bar(
                    stress_df,
                    x='Importance',
                    y='Feature',
                    orientation='h',
                    title='Feature Importance - Stress Model',
                    color='Importance',
                    color_continuous_scale='reds'
                )
                fig_stress_imp.update_layout(height=400)
                st.plotly_chart(fig_stress_imp, use_container_width=True)
            else:
                st.info("Feature importance data not available")
    
    # Model Training Information
    if model_summary:
        st.markdown("### 📈 Training Data Information")
        
        data_sources = model_summary.get('data_sources', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Data Volume")
            st.write(f"**Demand Records:** {data_sources.get('demand_records', 'N/A'):,}")
            st.write(f"**GenMix Records:** {data_sources.get('genmix_records', 'N/A'):,}")
        
        with col2:
            st.markdown("#### Date Range")
            date_range = data_sources.get('date_range', {})
            st.write(f"**Start:** {date_range.get('start', 'N/A')}")
            st.write(f"**End:** {date_range.get('end', 'N/A')}")
        
        with col3:
            st.markdown("#### Model Status")
            training_date = model_summary.get('training_completed_at', 'Unknown')
            if training_date != 'Unknown':
                training_dt = datetime.fromisoformat(training_date.replace('Z', '+00:00'))
                hours_since = (datetime.now() - training_dt.replace(tzinfo=None)).total_seconds() / 3600
                st.write(f"**Hours since training:** {hours_since:.1f}")
                
                # Training freshness indicator
                if hours_since < 24:
                    st.success("🟢 Recently trained")
                elif hours_since < 48:
                    st.warning("🟡 Training getting old")
                else:
                    st.error("🔴 Training may be stale")
    
    # Download options
    if predictions_data:
        st.markdown("### 💾 Export Predictions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Download Forecast Data (JSON)"):
                import json
                json_str = json.dumps(predictions_data, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"ml_predictions_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json"
                )
        
        with col2:
            if forecasts and len(forecasts) > 0:
                if st.button("📈 Download Forecast CSV"):
                    forecast_df = pd.DataFrame(forecasts)
                    csv_str = forecast_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv_str,
                        file_name=f"demand_forecast_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )
    
    # Footer info
    st.markdown("---")
    generation_time = predictions_data.get('generated_at', 'Unknown') if predictions_data else 'Unknown'
    st.markdown(f"**Predictions generated at:** {generation_time}")
    st.markdown("**Note:** Predictions are updated daily at 2:00 PM EST by the Azure ML Orchestrator") 