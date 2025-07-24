# File: components/filters.py
import streamlit as st
import pandas as pd

def sidebar_filters(schemes_df: pd.DataFrame, workflow_df: pd.DataFrame) -> dict:
    st.sidebar.header("Filters")

    # Ensure date columns are datetime
    if not pd.api.types.is_datetime64_any_dtype(schemes_df['creationDate']):
        schemes_df['creationDate'] = pd.to_datetime(schemes_df['creationDate'], errors='coerce')

    # Calculate min and max creation dates in data
    min_date = schemes_df['creationDate'].min()
    max_date = schemes_df['creationDate'].max()

    # Preset options for date ranges
    date_options = {
        "All Time": (min_date, max_date),
        "Past 1 Month": (max_date - pd.DateOffset(months=1), max_date),
        "Past 3 Months": (max_date - pd.DateOffset(months=3), max_date),
        "Past 6 Months": (max_date - pd.DateOffset(months=6), max_date),
        "Past 12 Months": (max_date - pd.DateOffset(months=12), max_date),
        "Past 2 Years": (max_date - pd.DateOffset(years=2), max_date),
        "Past 3 Years": (max_date - pd.DateOffset(years=3), max_date),
        "Past 5 Years": (max_date - pd.DateOffset(years=5), max_date),
        "Past 10 Years": (max_date - pd.DateOffset(years=10), max_date),
        "Custom Range": None  # Special option for custom range
    }

    # Dropdown selectbox for creation date range presets plus custom
    selected_range = st.sidebar.selectbox(
        "Creation Date Range",
        options=list(date_options.keys()),
        index=0
    )

    if selected_range == "Custom Range":
        # Custom range date pickers
        date_start = st.sidebar.date_input(
            "Start Date",
            min_value=min_date.date(),
            max_value=max_date.date(),
            value=min_date.date()
        )
        date_end = st.sidebar.date_input(
            "End Date",
            min_value=min_date.date(),
            max_value=max_date.date(),
            value=max_date.date()
        )
        if date_end < date_start:
            st.sidebar.error("Error: End Date must not be before Start Date.")
    else:
        date_start, date_end = date_options[selected_range]

    # Helper function to get sorted unique values or ['UNKNOWN'] if empty
    def get_sorted_unique(df_col):
        unique_vals = df_col.dropna().unique()
        if len(unique_vals) == 0:
            return ["UNKNOWN"]
        return sorted(unique_vals)

    # Multi-select filters for categorical fields with all selected by default
    plants = get_sorted_unique(schemes_df['plant'])
    selected_plants = st.sidebar.multiselect("Plant", plants, default=[])

    categories = get_sorted_unique(schemes_df['category'])
    selected_categories = st.sidebar.multiselect("Category", categories, default=[])

    departments = get_sorted_unique(schemes_df['department_at_time'])
    selected_departments = st.sidebar.multiselect("Department", departments, default=[])

    users = get_sorted_unique(workflow_df['user'])
    selected_users = st.sidebar.multiselect("User", users, default=[])

    # Return filters as dictionary
    filters = {
        "date_range": (pd.to_datetime(date_start), pd.to_datetime(date_end)),
        "plants": selected_plants,
        "categories": selected_categories,
        "departments": selected_departments,
        "users": selected_users,
    }

    return filters
