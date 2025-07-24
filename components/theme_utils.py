# File: components/theme_utils.py
import streamlit as st


def accessibility_options():
    """
    Provide user controls for accessibility options such as high-contrast mode and large text.
    """
    st.sidebar.markdown("### ♿ Accessibility")
    high_contrast = st.sidebar.checkbox("High Contrast Mode (bold colors)")
    large_text = st.sidebar.checkbox("Large Text")

    # Demo: Show accessibility status in main app area (alter app in main.py with these flags as needed)
    if high_contrast:
        st.markdown(
            "<style>body, .markdown-text-container, .css-1kwsnct {color: #000; background-color: #fff200 !important;}</style>",
            unsafe_allow_html=True
        )
        st.sidebar.success("High contrast enabled.")

    if large_text:
        st.markdown(
            "<style>html, body, [class*='css'] {font-size: 1.25em !important;}</style>",
            unsafe_allow_html=True
        )
        st.sidebar.success("Large text enabled.")

    # Return preferences as flags for further use (e.g., style widgets where needed)
    return high_contrast, large_text
