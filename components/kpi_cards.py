import streamlit as st

def render_kpis(filtered_schemes, workflow_df, attachments_df):
    col1, col2, col3 = st.columns(3)

    total_schemes = filtered_schemes["scheme_id"].nunique()
    total_users = filtered_schemes["createdBy"].nunique()
    total_attachments = attachments_df["fileName"].nunique()

    col1.metric("📦 Total Schemes", f"{total_schemes}")
    col2.metric("👤 Unique Creators", f"{total_users}")
    col3.metric("📎 Total Attachments", f"{total_attachments}")
