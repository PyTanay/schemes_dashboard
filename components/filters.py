# File: components/filters.py
import streamlit as st
import pandas as pd

def sidebar_filters(schemes_df: pd.DataFrame, workflow_df: pd.DataFrame) -> dict:
    st.sidebar.header("Filters")

    # Ensure creationDate is datetime
    if not pd.api.types.is_datetime64_any_dtype(schemes_df['creationDate']):
        schemes_df['creationDate'] = pd.to_datetime(schemes_df['creationDate'], errors='coerce')

    # Calculate overall date range
    min_date = schemes_df['creationDate'].min()
    max_date = schemes_df['creationDate'].max()

    # Date presets
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
        "Custom Range": None
    }

    # Filter mode
    filter_mode = st.sidebar.selectbox(
        "Filter Based On:",
        options=["Creation Info", "Workflow Path"],
        index=0
    )

    # Date Range input
    selected_range = st.sidebar.selectbox("Date Range", list(date_options.keys()))
    if selected_range == "Custom Range":
        date_start = st.sidebar.date_input("Start Date", min_value=min_date.date(), max_value=max_date.date(), value=min_date.date())
        date_end = st.sidebar.date_input("End Date", min_value=min_date.date(), max_value=max_date.date(), value=max_date.date())
        if date_end < date_start:
            st.sidebar.error("Error: End Date must not be before Start Date.")
    else:
        date_start, date_end = date_options[selected_range]

    selected_date_range = (pd.to_datetime(date_start), pd.to_datetime(date_end))

    # Helper for safely getting sorted unique values
    def get_sorted_unique(df_col):
        try:
            unique_vals = df_col.dropna().unique()
            return sorted(unique_vals) if len(unique_vals) > 0 else ["UNKNOWN"]
        except Exception:
            return ["UNKNOWN"]

    # =============== Filter Mode: WORKFLOW PATH ===============
    if filter_mode == "Workflow Path":
        workflow_df = workflow_df.copy()

        # Ensure datetime
        if 'forwarded_at' in workflow_df.columns:
            workflow_df['forwarded_at'] = pd.to_datetime(workflow_df['forwarded_at'], errors='coerce')

        # Department filter
        departments = get_sorted_unique(workflow_df['department'])
        selected_departments = st.sidebar.multiselect("Department", departments, default=[])

        # Filter users based on selected departments
        if selected_departments:
            filtered_users_df = workflow_df[workflow_df['department'].isin(selected_departments)]
        else:
            filtered_users_df = workflow_df

        users = get_sorted_unique(filtered_users_df['user'])
        selected_users = st.sidebar.multiselect("User", users, default=[])

        # Apply filters on workflow_df
        wf_filtered = workflow_df.copy()
        if selected_departments:
            wf_filtered = wf_filtered[wf_filtered['department'].isin(selected_departments)]
        if selected_users:
            wf_filtered = wf_filtered[wf_filtered['user'].isin(selected_users)]
        if 'forwarded_at' in wf_filtered.columns:
            wf_filtered = wf_filtered[
                (wf_filtered['forwarded_at'] >= selected_date_range[0]) &
                (wf_filtered['forwarded_at'] <= selected_date_range[1])
            ]

        # Get relevant scheme IDs
        relevant_scheme_ids = wf_filtered['scheme_id'].dropna().unique()
        schemes_df = schemes_df[schemes_df['scheme_id'].isin(relevant_scheme_ids)]

        # Filter categories based on resulting schemes
        filtered_categories_df = schemes_df
        categories = get_sorted_unique(filtered_categories_df['category'])
        selected_categories = st.sidebar.multiselect("Category", categories, default=[])

        if selected_categories:
            schemes_df = schemes_df[schemes_df['category'].isin(selected_categories)]

    # =============== Filter Mode: CREATION INFO ===============
    else:
        # Filter schemes by creationDate
        schemes_df = schemes_df[
            (schemes_df['creationDate'] >= selected_date_range[0]) &
            (schemes_df['creationDate'] <= selected_date_range[1])
        ]

        # Department filter
        departments = get_sorted_unique(schemes_df['department_at_time'])
        selected_departments = st.sidebar.multiselect("Department", departments, default=[])

        # Filter users based on selected departments
        if selected_departments:
            filtered_users_df = schemes_df[schemes_df['department_at_time'].isin(selected_departments)]
        else:
            filtered_users_df = schemes_df

        users = get_sorted_unique(filtered_users_df['createdBy'])
        selected_users = st.sidebar.multiselect("User", users, default=[])

        # Apply department filter
        if selected_departments:
            schemes_df = schemes_df[schemes_df['department_at_time'].isin(selected_departments)]
        # Apply user filter
        if selected_users:
            schemes_df = schemes_df[schemes_df['createdBy'].isin(selected_users)]

        # Category filter based on filtered schemes
        filtered_categories_df = schemes_df
        categories = get_sorted_unique(filtered_categories_df['category'])
        selected_categories = st.sidebar.multiselect("Category", categories, default=[])

        if selected_categories:
            schemes_df = schemes_df[schemes_df['category'].isin(selected_categories)]

    # Return dictionary of applied filters and filtered dataset
    filters = {
        "filter_mode": filter_mode,
        "date_range": selected_date_range,
        "categories": selected_categories,
        "departments": selected_departments,
        "users": selected_users,
        "filtered_schemes_df": schemes_df
    }

    return filters
