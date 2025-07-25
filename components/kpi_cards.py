import streamlit as st
import pandas as pd
import random
import hashlib

def safe_id(label, idx):
    h = hashlib.sha1(label.encode("utf-8")).hexdigest()[:6]
    return f"card{idx}_{h}"

def styled_kpi_card(label, value, icon, bg_rgba, bg_rgba_hover, card_id):
    # Font color for idle (light/bright)
    idle_font_color = "#FEFEFA"
    # Font color for hover (dark)
    hover_font_color = "#191919"
    st.markdown(
        f"""
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Rubik:wght@500&display=swap" rel="stylesheet">
        <style>
        .kpi-card-{card_id} {{
            background: {bg_rgba};
            border-radius: 19px;
            min-height: 176px; max-height: 176px; height: 176px;
            width: 100%; box-sizing: border-box;
            display: flex; flex-direction: column;
            justify-content: center; align-items: center; text-align: center;
            font-family: 'Montserrat', Arial, sans-serif;
            margin-bottom: 9px; padding: 22px 12px 14px 12px;
            box-shadow: 0 3px 16px rgba(30,40,55,0.12);
            transition: transform 0.18s, box-shadow 0.20s, background 0.22s, color 0.17s;
            color: {idle_font_color}; cursor: pointer;
            overflow: hidden; word-break: break-word;
        }}
        .kpi-card-{card_id} .kpi-label-{card_id},
        .kpi-card-{card_id} .kpi-value-{card_id},
        .kpi-card-{card_id} .kpi-icon-{card_id} {{
            color: {idle_font_color};
            transition: color 0.18s;
        }}
        .kpi-card-{card_id}:hover {{
            transform: scale(1.045);
            box-shadow:0 14px 32px rgba(24,48,99,0.22);
            background: {bg_rgba_hover};
        }}
        .kpi-card-{card_id}:hover .kpi-label-{card_id},
        .kpi-card-{card_id}:hover .kpi-value-{card_id},
        .kpi-card-{card_id}:hover .kpi-icon-{card_id} {{
            color: {hover_font_color} !important;
        }}
        .kpi-label-{card_id} {{
            font-size: 1.13rem; font-weight: 600;
            margin-bottom: 6px; opacity:0.97;
            font-family: 'Montserrat', Arial, sans-serif;
            white-space: normal; overflow-wrap: break-word;
        }}
        .kpi-value-{card_id} {{
            font-size: 2.27rem; font-weight: 700;
            font-family: 'Rubik', Arial, sans-serif;
            margin-top: 3px; letter-spacing: 0.14px;
            text-shadow: 0 2px 12px rgba(18,18,26,0.12);
            white-space: normal; overflow-wrap: break-word;
        }}
        .kpi-icon-{card_id} {{
            font-size: 1.45rem; margin-bottom: 7px;
            opacity: .83;
        }}
        </style>
        """, unsafe_allow_html=True
    )
    st.markdown(
        f'''
        <div class="kpi-card-{card_id}">
            <div class="kpi-icon-{card_id}">{icon}</div>
            <div class="kpi-label-{card_id}">{label}</div>
            <div class="kpi-value-{card_id}">{value}</div>
        </div>
        ''',
        unsafe_allow_html=True
    )

def display_kpi_cards(schemes_df, workflow_df, attachments_df):
    total_schemes = schemes_df['scheme_id'].nunique()
    avg_processing_time = workflow_df['time_taken'].mean()
    avg_processing_time_str = f"{avg_processing_time:.2f}" if not pd.isna(avg_processing_time) else "N/A"
    aging_over_180 = schemes_df[schemes_df['aging_bucket'] == '> 180 days']['scheme_id'].nunique()
    total_attachments = len(attachments_df)
    avg_attachments_per_scheme = (total_attachments / total_schemes) if total_schemes > 0 else 0

    if len(attachments_df) > 0 and len(workflow_df) > 0:
        wf_by_scheme = workflow_df.groupby('scheme_id')['time_taken'].sum()
        attach_by_scheme = attachments_df.groupby('scheme_id').size()
        merged = pd.DataFrame({'wf_time': wf_by_scheme, 'num_attach': attach_by_scheme})
        merged = merged[merged['num_attach'] > 0]
        merged['time_per_attachment'] = merged['wf_time'] / merged['num_attach']
        avg_time_per_attachment = merged['time_per_attachment'].mean()
    else:
        avg_time_per_attachment = 0

    unique_generators = schemes_df['createdBy'].nunique()
    unique_participators = workflow_df['user'].nunique()

    card_palettes = [
        ("rgba(54, 98, 165, 0.15)",  "rgba(54, 98, 165, 0.33)"),
        ("rgba(40, 151, 113, 0.15)", "rgba(40, 151, 113, 0.33)"),
        ("rgba(178, 55, 71, 0.16)",  "rgba(178, 55, 71, 0.33)"),
        ("rgba(222, 186, 67, 0.15)", "rgba(222, 186, 67, 0.31)"),
        ("rgba(124, 73, 157, 0.16)", "rgba(124, 73, 157, 0.33)"),
        ("rgba(21, 92, 154, 0.15)",  "rgba(21, 92, 154, 0.30)"),
        ("rgba(87, 194, 169, 0.13)", "rgba(87, 194, 169, 0.29)"),
        ("rgba(235, 104, 65, 0.15)", "rgba(235, 104, 65, 0.33)"),
    ]
    assigned_palettes = random.sample(card_palettes, len(card_palettes))

    card_data = [
        ("Total Schemes", total_schemes, "📄"),
        ("Avg Processing Time (hrs)", avg_processing_time_str, "⏳"),
        ("Schemes Aging >180 Days", aging_over_180, "⌛"),
        ("Total Attachments", total_attachments, "📎"),
        ("Avg Attachments/Scheme", f"{avg_attachments_per_scheme:.2f}", "🗂️"),
        ("Avg Time per Attachment (hrs)", f"{avg_time_per_attachment:.2f}", "⏱️"),
        ("Unique Scheme Creators", unique_generators, "🧑‍💻"),
        ("Unique Users in Flowpath", unique_participators, "🔗"),
    ]

    cols1 = st.columns(4)
    cols2 = st.columns(4)
    for i in range(4):
        bg, bg_hover = assigned_palettes[i]
        label, value, icon = card_data[i]
        card_id = safe_id(label, i)
        with cols1[i]:
            styled_kpi_card(label, value, icon, bg, bg_hover, card_id)
    for i in range(4, 8):
        bg, bg_hover = assigned_palettes[i]
        label, value, icon = card_data[i]
        card_id = safe_id(label, i)
        with cols2[i-4]:
            styled_kpi_card(label, value, icon, bg, bg_hover, card_id)
