import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_schemes
from streamlit_plotly_events import plotly_events

def line_chart_avg_time_over_time(workflow_df, start_date, end_date):
    st.subheader("📈 Avg. Time Taken per Scheme Over Time (Filtered)")

    filtered = workflow_df[
        (workflow_df["forwarded_at"] >= start_date) &
        (workflow_df["forwarded_at"] <= end_date)
    ].copy()

    if filtered.empty:
        st.info("No workflow data available for the selected date range.")
        return

    filtered["Month"] = filtered["forwarded_at"].dt.to_period("M")
    line_data = (
        filtered.groupby("Month")["time_taken"]
        .mean()
        .reset_index()
    )
    line_data["Month"] = line_data["Month"].dt.to_timestamp()

    # Determine unit
    avg_value = line_data["time_taken"].mean()
    unit = "days" if avg_value > 1 else "hours"

    fig = px.line(
        line_data,
        x="Month",
        y="time_taken",
        markers=True,
        title=f"Avg. Time Taken per Scheme Over Time ({unit})",
        labels={"Month": "Month-Year", "time_taken": f"Avg. Time Taken ({unit})"},
    )
    fig.update_traces(line_color="royalblue")
    fig.update_layout(
        xaxis_tickformat="%b %Y",
        xaxis_title="Month-Year",
        yaxis_title=f"Avg. Time Taken ({unit})",
        hovermode="x unified",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)




def histogram_time_taken(workflow_df, start_date, end_date):
    st.subheader("📊 Distribution of Avg. Time Taken per Scheme (Filtered)")

    workflow_df["forwarded_at"] = pd.to_datetime(workflow_df["forwarded_at"], errors='coerce')

    # Filter by date range
    filtered = workflow_df[
        (workflow_df["forwarded_at"] >= start_date) &
        (workflow_df["forwarded_at"] <= end_date)
    ].copy()

    if filtered.empty:
        st.info("No workflow data available for the selected date range.")
        return

    # Average time taken per scheme
    scheme_avg_time = (
        filtered.groupby("scheme_id")["time_taken"]
        .mean()
        .reset_index()
        .rename(columns={"time_taken": "avg_time_taken"})
    )

    # Limit to realistic range (0–10,000 hours)
    scheme_avg_time = scheme_avg_time[
        (scheme_avg_time["avg_time_taken"] >= 0) & (scheme_avg_time["avg_time_taken"] <= 10000)
    ]

    # Slider for selecting bin range
    min_val, max_val = 0, 10000
    selected_range = st.slider(
        "🎚️ Select Time Range (in hours) to Display Matching Schemes",
        min_value=min_val,
        max_value=max_val,
        value=(0, 1000),
        step=100
    )
    lower, upper = selected_range

    # Plot histogram
    fig = px.histogram(
        scheme_avg_time,
        x="avg_time_taken",
        nbins=100,
        title="Distribution of Avg. Time Taken per Scheme",
        labels={"avg_time_taken": "Avg. Time Taken (hours)"}
    )

    # Highlight selected range
    fig.update_layout(
        bargap=0.05,
        template="plotly_white",
        xaxis_title="Avg. Time Taken (hours)",
        yaxis_title="Number of Schemes",
        shapes=[
            dict(
                type="rect",
                xref="x", yref="paper",
                x0=lower, x1=upper,
                y0=0, y1=1,
                fillcolor="LightSkyBlue",
                opacity=0.3,
                layer="below",
                line_width=0,
            )
        ]
    )

    st.plotly_chart(fig, use_container_width=True)

    # Show filtered schemes within selected time range
    selected_schemes = scheme_avg_time[
        (scheme_avg_time["avg_time_taken"] >= lower) &
        (scheme_avg_time["avg_time_taken"] < upper)
    ]

    # Load scheme details
    schemes_df = load_schemes()

    # Merge for full display
    selected_merged = pd.merge(
        selected_schemes,
        schemes_df,
        on="scheme_id",
        how="left"
    )

        # Convert time from hours to days
    selected_merged["avg_time_taken_days"] = (selected_merged["avg_time_taken"] / 24).round(2)

    # Select columns to display
    display_columns = [
        "scheme_id",
        "plant",
        "category",
        "year",
        "short_description",
        "detailed_description",
        "createdBy",
        "avg_time_taken_days"
    ]

    selected_merged = selected_merged[display_columns].sort_values("avg_time_taken_days")
    selected_merged.rename(columns={"avg_time_taken_days": "Avg. Time Taken (days)"}, inplace=True)

    st.markdown(f"### 🧾 Schemes with Avg. Time Between **{lower} – {upper} hours**")
    st.dataframe(selected_merged)

def bar_chart_by_category(filtered_schemes_df):
    st.subheader("📊 Schemes by Category")

    if filtered_schemes_df.empty:
        st.info("No schemes available in the selected date range.")
        return

    # Count by category
    category_counts = filtered_schemes_df["category"].value_counts().reset_index()
    category_counts.columns = ["category", "count"]

    # Bar chart with colors
    fig = px.bar(
        category_counts,
        x="category",
        y="count",
        color="category",
        text="count",
        title="Number of Schemes per Category",
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig.update_layout(
        xaxis_title="Category",
        yaxis_title="Number of Schemes",
        template="plotly_white",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

def aging_bucket_bar_chart(pending_df):
    st.subheader("📊 Aging Bucket Distribution of Pending Schemes")
    counts = pending_df["aging_bucket"].value_counts().reindex(["< 90 days", "90–180 days", "> 180 days"])
    st.bar_chart(counts.fillna(0))
