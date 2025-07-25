# File: components/charts.py

import streamlit as st
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def line_avg_processing_time(workflow_df: pd.DataFrame):
    """
    Line chart for Average Processing Time Over Time (monthly).
    """
    if workflow_df.empty:
        st.info("No workflow data available for Average Processing Time chart.")
        return

    df = workflow_df.copy()
    if 'forwarded_at' not in df:
        st.warning("The workflow data is missing the 'forwarded_at' datetime column.")
        return
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
    Assumes workflow dataframe has 'department' and 'next_department' columns.
    """
    if workflow_df.empty:
        st.info("No workflow data available for Sankey diagram.")
        return

    df = workflow_df.copy()
    if 'next_department' not in df.columns or 'department' not in df.columns:
        st.warning("Sankey diagram requires 'department' and 'next_department' columns in workflow data.")
        return

    flow_counts = df.groupby(['department', 'next_department']).size().reset_index(name='count')
    all_nodes = list(pd.unique(flow_counts[['department', 'next_department']].values.ravel('K')))
    node_indices = {k: v for v, k in enumerate(all_nodes)}

    source_indices = flow_counts['department'].map(node_indices)
    target_indices = flow_counts['next_department'].map(node_indices)
    values = flow_counts['count']

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
    Bar chart showing distribution of schemes across aging buckets.
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

    df = workflow_df.groupby('user').agg(
        schemes_handled=('scheme_id', 'nunique'),
        avg_processing_time=('time_taken', 'mean')
    ).reset_index()

    import numpy as np
    if not df.empty and df['avg_processing_time'].nunique() > 1:
        df['performance'] = pd.qcut(df['avg_processing_time'], q=3, labels=["Fast", "Medium", "Slow"])
    else:
        df['performance'] = "N/A"

    # Optional: Use Streamlit-AgGrid if available, fallback to st.dataframe otherwise
    try:
        from st_aggrid import AgGrid
        from st_aggrid.grid_options_builder import GridOptionsBuilder
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
    Calendar heatmap for scheme inflow counts per day.
    """
    if schemes_df.empty:
        st.info("No scheme data available for Calendar Heatmap.")
        return

    inflow_counts = schemes_df.groupby('creationDate').size().reset_index(name='count')

    try:
        import calplot
        import matplotlib.pyplot as plt

        s = inflow_counts.set_index('creationDate')['count']
        fig, ax = plt.subplots(figsize=(16, 4))
        calplot.calplot(s, cmap='YlGn', fill_between=True, ax=ax)
        plt.title('Scheme Inflow Calendar Heatmap')
        st.pyplot(fig)
    except ImportError:
        st.warning("For calendar heatmap, install 'calplot' (pip install calplot) and matplotlib for enhanced visualization.")

def big_button(label, key, width="56px", height="44px", font_size="2.1rem"):
    """Render a visually large, clickable button with provided label."""
    # Using a form to handle button pressed event in one block
    pressed = st.markdown(
        f"""
        <button type="submit" name="{key}" style='
            width:{width};
            height:{height};
            font-size:{font_size};
            border-radius:10px;
            border:none;
            background:#314866;
            color:white;
            margin:1px 8px 1px 8px;
            padding:0;
            box-shadow:0 1px 4px #0001;
            transition:background 0.13s;'
            onmouseover="this.style.background='#48638c'" 
            onmouseout="this.style.background='#314866'"
        >{label}</button>
        """,
        unsafe_allow_html=True,
    )
    # This returns None; just for layout.
    return False

def histogram_avg_time_bins(schemes_df: pd.DataFrame, workflow_df: pd.DataFrame):
    avg_time_df = workflow_df.groupby("scheme_id")['time_taken'].mean().reset_index()
    avg_time_df.rename(columns={'time_taken': 'avg_time_taken'}, inplace=True)
    merged = schemes_df.merge(avg_time_df, on="scheme_id")
    times = merged['avg_time_taken'].dropna()

    if times.empty:
        st.info("No data available for average processing time histogram.")
        return

    min_time = int(np.floor(times.min()))
    max_time = int(np.ceil(times.max()))
    bins_key = "histogram_bin_count"
    range_key = "histogram_range"

    if bins_key not in st.session_state:
        st.session_state[bins_key] = 15
    if range_key not in st.session_state:
        st.session_state[range_key] = (min_time, max_time)

    # Title above the number of bins input box
    st.markdown("<div style='font-weight:600; font-size:1.1rem; margin-bottom:4px;'>Number of bins</div>", unsafe_allow_html=True)

    # Number of bins input textbox
    bins_val = st.text_input(
        label="",
        value=str(st.session_state[bins_key]),
        max_chars=3,
        key="bins_val",
        help="Enter number of bins between 5 and 100",
        label_visibility="collapsed",
        )
    # Validate and clamp the input
    if bins_val.isdigit():
        manual_val = min(100, max(5, int(bins_val)))
        if manual_val != st.session_state[bins_key]:
            st.session_state[bins_key] = manual_val
    num_bins = st.session_state[bins_key]

    # Timespan slider below the chart
    hist_range = st.session_state[range_key]

    # Compute visible data based on hist_range
    visible_times = times[(times >= hist_range[0]) & (times <= hist_range[1])] if hist_range[0] < hist_range[1] else times
    hist, bins = np.histogram(visible_times, bins=num_bins, range=hist_range)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    merged_visible = merged[(merged['avg_time_taken'] >= hist_range[0]) & (merged['avg_time_taken'] <= hist_range[1])]
    bin_indices = np.digitize(merged_visible['avg_time_taken'], bins, right=False) - 1

    # Plot histogram
    fig = px.bar(
        x=bin_centers,
        y=hist,
        labels={'x': 'Average Processing Time (hrs, per scheme)', 'y': 'Number of Schemes'},
        text_auto=True
    )
    fig.update_traces(marker_color='rgb(58,104,230)')
    fig.update_layout(
        title="Number of Schemes vs Average Time Taken",
        xaxis_title="Average Processing Time (hrs, per scheme)",
        yaxis_title="Number of Schemes",
        bargap=0.15,
        xaxis=dict(range=[hist_range[0], hist_range[1]], tickformat="d"),
        font=dict(color="#eee"),
        height=375,
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})

    # Display timespan selector slider below the chart
    new_hist_range = st.slider(
        "Select timespan range for histogram (hrs):",
        min_value=min_time,
        max_value=max_time,
        value=hist_range,
        step=1,
        format="%d"
    )
    st.session_state[range_key] = new_hist_range

    # Update histogram and bin scheme lists according to new selections
    visible_times = times[(times >= new_hist_range[0]) & (times <= new_hist_range[1])]
    hist, bins = np.histogram(visible_times, bins=num_bins, range=new_hist_range)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    merged_visible = merged[
        (merged['avg_time_taken'] >= new_hist_range[0]) & (merged['avg_time_taken'] <= new_hist_range[1])
    ]
    bin_indices = np.digitize(merged_visible['avg_time_taken'], bins, right=False) - 1
    schemes_by_bin = {i: merged_visible[bin_indices == i] for i in range(num_bins)}

    bin_labels = [
        f"{bins[i]:.0f} - {bins[i+1]:.0f} hrs ({hist[i]} schemes)" for i in range(num_bins)
    ]

    selected_bin = st.selectbox(
        "Select a bin to view scheme details",
        options=list(range(num_bins)),
        format_func=lambda i: bin_labels[i]
    )

    selected_schemes = schemes_by_bin[selected_bin]
    st.markdown(f"### Schemes in Bin {bin_labels[selected_bin]}")
    if selected_schemes.empty:
        st.write("No schemes in this bin.")
    else:
        possible_titles = ['title', 'scheme_title', 'name', 'Scheme Title']
        title_col = next((c for c in possible_titles if c in selected_schemes.columns), None)
        base_cols = ['scheme_id','short_description', 'avg_time_taken', 'createdBy', 'plant', 'category', 'department_at_time']
        show_cols = (['scheme_id', title_col] + base_cols[1:]) if title_col else base_cols
        show_cols = [c for c in show_cols if c in selected_schemes.columns]
        st.dataframe(selected_schemes[show_cols].reset_index(drop=True))