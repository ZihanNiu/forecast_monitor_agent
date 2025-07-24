"""
Streamlit app for forecast monitoring agent.
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from modules.loader import load_data, get_item_data, get_all_item_ids, get_recent_actuals, get_early_forecast
from modules.diagnostics import run_all_diagnostics
from modules.visualizer import plot_forecast_analysis, create_summary_stats_table
from modules.explainer import prepare_analysis_summary, generate_explanation, format_explanation_report
from modules.reporter import create_detailed_report


def main():
    st.set_page_config(page_title="Forecast Monitor Agent", layout="wide")
    
    st.title("🔍 Forecast Monitor Agent")
    st.markdown("Intelligent detection and explanation of forecast alignment issues")
    
    # Load data
    try:
        df = load_data("data/data.csv")
        item_ids = get_all_item_ids(df)
        
        st.sidebar.header("Configuration")
        selected_item = st.sidebar.selectbox("Select Item ID", item_ids)
        
        if selected_item:
            # Load item data
            historical_data, forecast_data = get_item_data(df, selected_item)
            recent_actuals = get_recent_actuals(historical_data)
            early_forecast = get_early_forecast(forecast_data)
            
            # Run diagnostics
            diagnostics = run_all_diagnostics(historical_data, forecast_data, recent_actuals, early_forecast)
            
            # Create explanation
            analysis_summary = prepare_analysis_summary(selected_item, diagnostics, historical_data, forecast_data)
            explanation = generate_explanation(analysis_summary, use_mock=True)
            report = format_explanation_report(selected_item, diagnostics, explanation)
            
            # Display results
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📊 Time Series Analysis")
                
                # Create and display plot
                fig = plot_forecast_analysis(historical_data, forecast_data, diagnostics, selected_item)
                st.pyplot(fig)
                plt.close()
                
                # Summary statistics
                st.subheader("📈 Summary Statistics")
                stats_df = create_summary_stats_table(historical_data, forecast_data)
                st.dataframe(stats_df, use_container_width=True)
            
            with col2:
                st.subheader("🚨 Issue Detection")
                
                # Risk score
                risk_score = report['risk_score']
                if risk_score > 0.5:
                    st.error(f"🔴 High Risk: {risk_score:.3f}")
                elif risk_score > 0.2:
                    st.warning(f"🟡 Medium Risk: {risk_score:.3f}")
                else:
                    st.success(f"🟢 Low Risk: {risk_score:.3f}")
                
                # Issues summary
                st.metric("Issues Detected", report['total_issues'])
                st.metric("Avg Confidence", f"{report['avg_confidence']:.3f}")
                
                # Individual issues
                issues = diagnostics
                
                if issues['trend_mismatch']['detected']:
                    st.error(f"❌ Trend Mismatch ({issues['trend_mismatch']['confidence']:.2f})")
                
                if issues['missing_seasonality']['detected']:
                    st.error(f"❌ Missing Seasonality ({issues['missing_seasonality']['confidence']:.2f})")
                
                if issues['volatility_mismatch']['detected']:
                    st.error(f"❌ Too Flat ({issues['volatility_mismatch']['confidence']:.2f})")
                
                if issues['magnitude_mismatch']['detected']:
                    st.error(f"❌ Magnitude Mismatch ({issues['magnitude_mismatch']['confidence']:.2f})")
                
                if report['total_issues'] == 0:
                    st.success("✅ No issues detected")
            
            # Explanation section
            st.subheader("🤖 AI Explanation")
            st.info(explanation)
            
            # Detailed diagnostics (expandable)
            with st.expander("🔍 Detailed Diagnostics"):
                detailed_report = create_detailed_report(report)
                st.text(detailed_report)
            
            # Data preview (expandable)
            with st.expander("📋 Data Preview"):
                st.write("**Historical Data (last 10 months):**")
                st.write(historical_data.tail(10))
                st.write("**Forecast Data (first 10 months):**")
                st.write(forecast_data.head(10))
    
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'data/data.csv' exists.")
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")


if __name__ == "__main__":
    main()