# streamlit_app.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Load data
workflow = pd.read_csv("workflow.csv", parse_dates=['forwarded_at'])
attachments = pd.read_csv("attachments.csv")
schemes = pd.read_csv("schemes.csv", parse_dates=['creationDate'])

# Merge all on scheme_id
merged = schemes.merge(workflow, on="scheme_id", how="left")
merged = merged.merge(attachments, on="scheme_id", how="left")

# Sidebar filters
st.sidebar.header("Filters")

# --- Date Filters --- #
date_filter_type = st.sidebar.selectbox(
    "Time Period",
    ["All Time", "Past 1 Month", "Past 3 Months", "Past 6 Months", "Past 12 Months", "Past 3 Years", "Past 5 Years", "Past 10 Years", "Custom"]
)

now = pd.Timestamp.now()

if date_filter_type == "Custom":
    start_date = st.sidebar.date_input("Start Date", value=now - timedelta(days=180))
    end_date = st.sidebar.date_input("End Date", value=now)
else:
    if date_filter_type == "All Time":
        start_date = schemes["creationDate"].min()
        end_date = schemes["creationDate"].max()
    elif "Month" in date_filter_type:
        months = int(date_filter_type.split()[1])
        start_date = now - pd.DateOffset(months=months)
        end_date = now
    elif "Year" in date_filter_type:
        years = int(date_filter_type.split()[1])
        start_date = now - pd.DateOffset(years=years)
        end_date = now

# Filter by date range
filtered = merged[(merged["creationDate"] >= pd.to_datetime(start_date)) & (merged["creationDate"] <= pd.to_datetime(end_date))]

# Optional Filters
plants = st.sidebar.multiselect("Plant", options=sorted(merged["plant"].dropna().unique()), default=None)
categories = st.sidebar.multiselect("Category", options=sorted(merged["category"].dropna().unique()), default=None)
designations = st.sidebar.multiselect("Designation", options=sorted(merged["designation_at_time"].dropna().unique()), default=None)

if plants:
    filtered = filtered[filtered["plant"].isin(plants)]
if categories:
    filtered = filtered[filtered["category"].isin(categories)]
if designations:
    filtered = filtered["designation"].isin(designations)

# --- Dashboard --- #
st.title("🧠 Scheme Monitoring Dashboard")

col1, col2, col3 = st.columns(3)
col1.metric("Total Schemes", filtered["scheme_id"].nunique())
col2.metric("Total Attachments", filtered["fileName"].nunique())
st.write("Filtered columns:", filtered.columns.tolist())
col3.metric("Users Involved", filtered["createdBy"].nunique())

st.markdown("---")

# Time trend
st.subheader("📈 Scheme Creation Over Time")
time_series = filtered.groupby(filtered["creationDate"].dt.to_period("M")).size().rename("Scheme Count").reset_index()
time_series["creationDate"] = time_series["creationDate"].dt.to_timestamp()
st.line_chart(time_series.set_index("creationDate"))

# Bar chart - Schemes by Category
st.subheader("📊 Schemes by Category")
category_counts = filtered["category"].value_counts()
st.bar_chart(category_counts)

# Table preview
st.subheader("📋 Filtered Scheme Details")
st.dataframe(filtered[["scheme_id", "plant", "category", "creationDate", "createdBy", "designation_at_time", "fileName"]].drop_duplicates())
