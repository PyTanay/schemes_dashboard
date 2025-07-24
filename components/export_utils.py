import streamlit as st
import pandas as pd

def make_export_buttons(df: pd.DataFrame, label_prefix: str = "Export Data"):
    """
    Display buttons for exporting a DataFrame as CSV and Excel.

    Args:
        df: DataFrame to be exported
        label_prefix: Label used for button text
    """

    # Convert DataFrame to CSV/Excel in-memory for download
    csv = df.to_csv(index=False).encode('utf-8')
    xlsx = None
    try:
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        xlsx = output.getvalue()
    except ImportError:
        xlsx = None  # Excel download unavailable (xlsxwriter not installed)

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            label=f"{label_prefix} (CSV)",
            data=csv,
            file_name="dashboard_export.csv",
            mime='text/csv'
        )
    with c2:
        if xlsx:
            st.download_button(
                label=f"{label_prefix} (Excel)",
                data=xlsx,
                file_name="dashboard_export.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            st.info("Install xlsxwriter for Excel downloads.")

    # Optional: Add easy clipboard copy or link-sharing here as desired.
