import streamlit as st
from utils.data_loader import load_data
from utils.calculations import average_processing_time, determine_pending_owners
from components.filters import get_filters
from components.kpi_cards import render_kpis
from components.charts import (
    line_chart_avg_time_over_time,
    histogram_time_taken,
    bar_chart_by_category
)
from utils.calculations import classify_aging_buckets
from components.charts import aging_bucket_bar_chart

# ------------------------------------------
# 🚀 Streamlit Setup
# ------------------------------------------
st.set_page_config(page_title="📊 Scheme KPI Dashboard", layout="wide")
st.title("📊 Scheme Performance Dashboard")

# ------------------------------------------
# 📥 Load Data
# ------------------------------------------
schemes_df, workflow_df, attachments_df, merged_df = load_data()

# ------------------------------------------
# 🧭 Sidebar Filters
# ------------------------------------------
start_date, end_date, plants, categories, departments = get_filters(schemes_df)

# Apply filters to schemes
filtered = schemes_df[
    (schemes_df["creationDate"] >= start_date) &
    (schemes_df["creationDate"] <= end_date)
]
if plants:
    filtered = filtered[filtered["plant"].isin(plants)]
if categories:
    filtered = filtered[filtered["category"].isin(categories)]
if departments:
    filtered = filtered[filtered["department_at_time"].isin(departments)]

# ------------------------------------------
# 📊 KPI Cards
# ------------------------------------------
render_kpis(filtered, workflow_df, attachments_df)

# ------------------------------------------
# 📈 Charts
# ------------------------------------------
line_chart_avg_time_over_time(workflow_df, start_date, end_date)
histogram_time_taken(workflow_df, start_date, end_date)
bar_chart_by_category(filtered)
# ------------------------------------------
# ⌛ Aging Buckets
# ------------------------------------------
st.markdown("---")
st.header("🕓 Scheme Aging Analysis")

pending_df = classify_aging_buckets(schemes_df, workflow_df, end_date)
aging_bucket_bar_chart(pending_df)

with st.expander("🧾 Pending Scheme Aging Detail"):
    st.dataframe(pending_df[["scheme_id", "user", "department", "creationDate", "forwarded_at", "aging_days", "aging_bucket"]])


# ------------------------------------------
# 📝 Optional: Show filtered data preview
# ------------------------------------------
with st.expander("🔎 View Filtered Scheme Details"):
    st.dataframe(filtered.sort_values("creationDate", ascending=False))
