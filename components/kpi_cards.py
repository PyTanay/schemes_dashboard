# File: components/kpi_cards.py
import streamlit as st
import pandas as pd

def display_kpi_cards(schemes_df: pd.DataFrame, workflow_df: pd.DataFrame, attachments_df: pd.DataFrame):
    """
    Display the main KPI cards in the dashboard.

    KPIs:
    - Total Schemes Handled
    - Average Processing Time (hours)
    - Schemes Aging > 180 days
    - Total Attachments Uploaded
    """

    col1, col2, col3, col4 = st.columns(4)

    # Total schemes handled (unique scheme_id count)
    total_schemes = schemes_df['scheme_id'].nunique()

    # Average processing time from workflow, handle missing gracefully
    avg_processing_time = workflow_df['time_taken'].mean()
    avg_processing_time_str = f"{avg_processing_time:.2f}" if not pd.isna(avg_processing_time) else "N/A"

    # Schemes aging > 180 days
    aging_over_180 = schemes_df[schemes_df['aging_bucket'] == '> 180 days']['scheme_id'].nunique()

    # Total attachments uploaded
    total_attachments = len(attachments_df)

    # Display KPI cards
    col1.metric(label="Total Schemes Handled", value=f"{total_schemes}")
    col2.metric(label="Avg Processing Time (hrs)", value=avg_processing_time_str)
    col3.metric(label="Schemes Aging > 180 Days", value=f"{aging_over_180}")
    col4.metric(label="Total Attachments Uploaded", value=f"{total_attachments}")
