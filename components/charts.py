# File: components/charts.py
import streamlit as st
import plotly.express as px
import pandas as pd

def line_avg_processing_time(workflow_df: pd.DataFrame):
    """
    Line chart for Average Processing Time Over Time (monthly).
    """
    if workflow_df.empty:
        st.info("No workflow data available for Average Processing Time chart.")
        return

    df = workflow_df.copy()
    df['month'] = df['forwarded_at'].dt.to_period('M').dt.to_timestamp()
    avg_time = df.groupby('month')['time_taken'].mean().reset_index()

    fig = px.line(
        avg_time,
        x='month',
        y='time_taken',
        title='Average Processing Time Over Time',
        labels={'time_taken': 'Avg Processing Time (hours)', 'month': 'Month'},
        markers=True,
    )
    fig.update_layout(transition_duration=500)

    st.plotly_chart(fig, use_container_width=True)

def bar_scheme_count_by_category(schemes_df: pd.DataFrame):
    """
    Bar chart for Scheme Count by Category.
    """
    if schemes_df.empty:
        st.info("No scheme data available for Scheme Count by Category chart.")
        return

    counts = schemes_df['category'].value_counts().reset_index()
    counts.columns = ['category', 'count']

    fig = px.bar(
        counts,
        x='category',
        y='count',
        title='Scheme Count by Category',
        labels={'count': 'Number of Schemes', 'category': 'Category'},
        text='count'
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(yaxis=dict(range=[0, counts['count'].max()*1.1]), transition_duration=500)

    st.plotly_chart(fig, use_container_width=True)

def sankey_scheme_flow(workflow_df: pd.DataFrame):
    """
    Sankey diagram to visualize scheme flow between departments.
    Assumes workflow dataframe has 'department' and 'next_department' or similar.
    """

    # Example logic - workflow should have 'department' and the next step's department to show flow
    # You may need to prepare this data earlier if not present.

    if workflow_df.empty:
        st.info("No workflow data available for Sankey diagram.")
        return

    # Prepare nodes and links
    df = workflow_df.copy()

    # For example purposes, assume df has columns ['department', 'next_department']
    # If not, you may need to generate next_department column before

    if 'next_department' not in df.columns:
        st.warning("Sankey diagram requires 'next_department' column in workflow data.")
        return

    # Count flow occurrences
    flow_counts = df.groupby(['department', 'next_department']).size().reset_index(name='count')

    # Create list of unique nodes
    all_nodes = list(pd.unique(flow_counts[['department', 'next_department']].values.ravel('K')))
    node_indices = {k: v for v, k in enumerate(all_nodes)}

    source_indices = flow_counts['department'].map(node_indices)
    target_indices = flow_counts['next_department'].map(node_indices)
    values = flow_counts['count']

    import plotly.graph_objects as go

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=all_nodes,
            color="blue"
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values
        )
    )])

    fig.update_layout(title_text="Scheme Flow Between Departments", font_size=10, transition_duration=500)
    st.plotly_chart(fig, use_container_width=True)

def aging_bucket_distribution(schemes_df: pd.DataFrame):
    """
    Bar chart or heatmap showing distribution of schemes across aging buckets.
    """
    if schemes_df.empty:
        st.info("No scheme data available for aging bucket distribution.")
        return

    counts = schemes_df['aging_bucket'].value_counts().reindex(
        ["< 90 days", "90–180 days", "> 180 days"], fill_value=0
    ).reset_index()
    counts.columns = ['Aging Bucket', 'Count']

    fig = px.bar(
        counts,
        x='Aging Bucket',
        y='Count',
        title='Scheme Aging Bucket Distribution',
        color='Aging Bucket',
        color_discrete_map={
            "< 90 days": "green",
            "90–180 days": "orange",
            "> 180 days": "red"
        },
        text='Count'
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(yaxis=dict(range=[0, counts['Count'].max()*1.1]), transition_duration=500)

    st.plotly_chart(fig, use_container_width=True)

def performance_matrix(workflow_df: pd.DataFrame):
    """
    Table showing performance metrics per user or department with highlighting.
    """
    if workflow_df.empty:
        st.info("No workflow data available for Performance Matrix.")
        return

    # Example aggregation by user
    df = workflow_df.groupby('user').agg(
        schemes_handled=('scheme_id', 'nunique'),
        avg_processing_time=('time_taken', 'mean')
    ).reset_index()

    # Highlight top and slowest performers
    import numpy as np
    df['performance'] = pd.qcut(df['avg_processing_time'], q=3, labels=["Fast", "Medium", "Slow"])

    # Use Streamlit AgGrid for enhanced interactivity if installed, else fallback
    try:
        from st_aggrid import AgGrid, GridOptionsBuilder
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_side_bar()
        gb.configure_default_column(editable=False, groupable=True)
        grid_options = gb.build()
        AgGrid(df, gridOptions=grid_options, enable_enterprise_modules=False)
    except ImportError:
        st.dataframe(df)

    st.markdown("""
    - **Fast**: Lower processing times (better performers)<br>
    - **Slow**: Higher processing times (need focus)<br>
    """)

def calendar_heatmap_inflow_outflow(schemes_df: pd.DataFrame):
    """
    Calendar heatmap for scheme inflow/outflow counts per day.
    This is a complex visualization; you may consider external libraries or custom logic.
    For simplicity, here just show inflow counts heatmap by creationDate.
    """
    if schemes_df.empty:
        st.info("No scheme data available for Calendar Heatmap.")
        return

    inflow_counts = schemes_df.groupby('creationDate').size().reset_index(name='count')

    # Use Plotly to create a calendar heatmap approximation using a heatmap over weeks vs weekdays
    try:
        import calplot
    except ImportError:
        st.warning("For calendar heatmap, install 'calplot' (pip install calplot) for enhanced visualization.")
        return

    # calplot expects a pd.Series indexed by date
    s = inflow_counts.set_index('creationDate')['count']

    import matplotlib.pyplot as plt
    import calplot

    fig, ax = plt.subplots(figsize=(16, 4))
    calplot.calplot(s, cmap='YlGn', fill_between=True, ax=ax)
    plt.title('Scheme Inflow Calendar Heatmap')
    st.pyplot(fig)
