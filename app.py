# File: app.py

import streamlit as st
import pandas as pd

# Import your utility modules and components
from utils.data_loader import load_schemes, load_workflow, load_attachments, load_health_metrics
from components.filters import sidebar_filters
from components.kpi_cards import display_kpi_cards
from components.charts import (
    line_avg_processing_time,
    bar_scheme_count_by_category,
    sankey_scheme_flow,
    aging_bucket_distribution,
    performance_matrix,
    histogram_avg_time_bins,

)
from components.data_health import display_data_health
from components.theme_utils import  accessibility_options  # optional

# Filtering function that respects empty selections as "no filter" on those fields
def filter_data(schemes, workflow, attachments, filters):
    start_date, end_date = filters["date_range"]

    # Filter schemes by main criteria
    filtered_schemes = schemes[
        (schemes['creationDate'] >= pd.to_datetime(start_date)) &
        (schemes['creationDate'] <= pd.to_datetime(end_date))
    ]
    if filters["plants"]:
        filtered_schemes = filtered_schemes[filtered_schemes['plant'].isin(filters["plants"])]
    if filters["categories"]:
        filtered_schemes = filtered_schemes[filtered_schemes['category'].isin(filters["categories"])]
    if filters["departments"]:
        filtered_schemes = filtered_schemes[filtered_schemes['department_at_time'].isin(filters["departments"])]
    
    # Filter workflow
    filtered_workflow = workflow.copy()
    if filters["users"]:
        filtered_workflow = filtered_workflow[filtered_workflow['user'].isin(filters["users"])]
    if filters["departments"]:
        filtered_workflow = filtered_workflow[filtered_workflow['department'].isin(filters["departments"])]
    # New: Only keep workflow steps relating to visible schemes
    if not filtered_schemes.empty:
        filtered_workflow = filtered_workflow[filtered_workflow['scheme_id'].isin(filtered_schemes['scheme_id'])]
    
    # Filter attachments table by both user and scheme_id in filtered schemes
    filtered_attachments = attachments[attachments['scheme_id'].isin(filtered_schemes['scheme_id'])]
    if filters["users"]:
        filtered_attachments = filtered_attachments[filtered_attachments['user'].isin(filters["users"])]
    
    return filtered_schemes, filtered_workflow, filtered_attachments




def main():
    # Configure page
    st.set_page_config(
        page_title="Scheme Lifecycle Management Dashboard",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Optionally activate theme and accessibility toggles
    # _high_contrast, _large_text = accessibility_options()

    st.title("🚀 Scheme Lifecycle Management Dashboard")

    # Load cleaned datasets
    schemes = load_schemes()
    workflow = load_workflow()
    attachments = load_attachments()
    data_health = load_health_metrics()

    # Sidebar: get filters dictionary
    filters = sidebar_filters(schemes, workflow)

    # Filter data according to current filters
    filtered_schemes, filtered_workflow, filtered_attachments = filter_data(schemes, workflow, attachments, filters)

    # Display KPIs
    display_kpi_cards(filtered_schemes, filtered_workflow, filtered_attachments)

    # Main tabs for organization
    tabs = st.tabs(["Overview", "Performance", "Scheme Flow", "Aging Analysis", "Data Health", "Detailed Data"])

    with tabs[0]:
        st.header("📈 Overview")
        line_avg_processing_time(filtered_workflow)
        bar_scheme_count_by_category(filtered_schemes)
        histogram_avg_time_bins(filtered_schemes, filtered_workflow)


    with tabs[1]:
        st.header("🏆 Performance")
        performance_matrix(filtered_workflow)

    with tabs[2]:
        st.header("🔄 Scheme Flow")
        sankey_scheme_flow(filtered_workflow)

    with tabs[3]:
        st.header("⏳ Aging Analysis")
        aging_bucket_distribution(filtered_schemes)

    with tabs[4]:
        st.header("⚠️ Data Quality & Health")
        display_data_health(data_health)

    with tabs[5]:
        st.header("📋 Detailed Scheme Data")
        st.dataframe(filtered_schemes.reset_index(drop=True))

    # Footer / last updated or attribution
    st.markdown("---")
    st.caption("Created by Tanay.")

if __name__ == "__main__":
    main()
