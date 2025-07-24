# File: components/data_health.py
import streamlit as st

def display_data_health(health_metrics: dict):
    """
    Display key data quality and health checks in the dashboard.

    The `health_metrics` dict is expected to contain keys such as:
        - schemes_missing_scheme_id
        - schemes_missing_creationDate
        - schemes_missing_category
        - workflow_missing_scheme_id
        - attachments_missing_scheme_id
        - schemes_aging_gt_180
        - duplicates, etc.

    Adapt keys/labels as per your preprocessing output.
    """

    if not health_metrics:
        st.info("No data health metrics available to display.")
        return

    st.markdown("### ⚠️ Data Quality & Health Summary")

    # Prepare a user-friendly mapping between metric keys and descriptive labels
    metric_labels = {
        "schemes_missing_scheme_id": "Schemes Missing Scheme ID",
        "schemes_missing_creationDate": "Schemes Missing Creation Date",
        "schemes_missing_category": "Schemes Missing Category",
        "schemes_missing_department": "Schemes Missing Department",
        "workflow_missing_scheme_id": "Workflow Entries Missing Scheme ID",
        "workflow_missing_forwarded_at": "Workflow Entries Missing Forward Date",
        "workflow_missing_time_taken": "Workflow Entries Missing Time Taken",
        "attachments_missing_scheme_id": "Attachments Missing Scheme ID",
        "attachments_missing_fileName": "Attachments Missing File Name",
        "schemes_duplicate_scheme_id": "Duplicate Scheme IDs",
        "workflow_duplicate_rows": "Duplicate Workflow Entries",
        "attachments_duplicate_rows": "Duplicate Attachment Entries",
        "schemes_aging_gt_180": "Schemes Aging Over 180 Days",
    }

    # Convert the health_metrics dict to a list of (label, count) tuples
    health_items = [(metric_labels.get(k, k), v) for k, v in health_metrics.items()]

    # Sort so that highest counts appear on top (optional)
    health_items.sort(key=lambda x: (x[1] if isinstance(x[1], (int, float)) else 0), reverse=True)

    # Display in a table-like format
    st.table(
        {"Metric": [item[0] for item in health_items], "Count": [item[1] for item in health_items]}
    )

    # Additional actionable messages
    if health_metrics.get("schemes_aging_gt_180", 0) > 0:
        st.warning(f"There are {health_metrics['schemes_aging_gt_180']} schemes aging over 180 days. Consider investigating delays.")

    missing_id_total = sum(
        health_metrics.get(k, 0)
        for k in [
            "schemes_missing_scheme_id",
            "workflow_missing_scheme_id",
            "attachments_missing_scheme_id",
        ]
    )
    if missing_id_total > 0:
        st.error(f"Attention: There are {missing_id_total} records missing Scheme IDs across your datasets.")

    # You can expand this section with custom suggestions or links to documentation

