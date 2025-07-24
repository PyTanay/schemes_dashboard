import streamlit as st
from datetime import timedelta
import pandas as pd

def get_filters(schemes_df):
    now = pd.Timestamp.now()

    # Sidebar Controls
    st.sidebar.header("🔍 Filters")
    date_filter_type = st.sidebar.selectbox(
        "Time Period",
        ["All Time", "Past 1 Month", "Past 3 Months", "Past 6 Months", "Past 12 Months", "Past 3 Years", "Past 5 Years", "Custom"]
    )

    if date_filter_type == "Custom":
        start_date = st.sidebar.date_input("Start Date", value=now - timedelta(days=180))
        end_date = st.sidebar.date_input("End Date", value=now)
    else:
        offset = pd.DateOffset(months=int(date_filter_type.split()[1])) if "Month" in date_filter_type else pd.DateOffset(years=int(date_filter_type.split()[1])) if "Year" in date_filter_type else None
        start_date = now - offset if offset else schemes_df["creationDate"].min()
        end_date = now

    plants = st.sidebar.multiselect("Plant", options=sorted(schemes_df["plant"].dropna().unique()))
    categories = st.sidebar.multiselect("Category", options=sorted(schemes_df["category"].dropna().unique()))
    departments = st.sidebar.multiselect("Department", options=sorted(schemes_df["department_at_time"].dropna().unique()))

    return pd.to_datetime(start_date), pd.to_datetime(end_date), plants, categories, departments
