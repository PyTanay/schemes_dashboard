import os
import pandas as pd

# --- Configuration ---
DATA_DIR = r"D:\Automation\python\schemes_dashboard\data"

# --- Core Loaders ---

def load_schemes(clean=True):
    """Load (cleaned) schemes data with enriched columns for dashboard."""
    fname = "schemes_cleaned.csv" if clean else "schemes.csv"
    fpath = os.path.join(DATA_DIR, fname)
    df = pd.read_csv(fpath, parse_dates=["creationDate"])
    if clean and "last_action_date" in df.columns:
        df["last_action_date"] = pd.to_datetime(df["last_action_date"])
    return df

def load_workflow(clean=True):
    """Load (cleaned) workflow data."""
    fname = "workflow_cleaned.csv" if clean else "workflow.csv"
    fpath = os.path.join(DATA_DIR, fname)
    df = pd.read_csv(fpath, parse_dates=["forwarded_at"])
    return df

def load_attachments(clean=True):
    """Load (cleaned) attachments data."""
    fname = "attachments_cleaned.csv" if clean else "attachments.csv"
    fpath = os.path.join(DATA_DIR, fname)
    df = pd.read_csv(fpath)
    return df

# --- Summary & Pre-aggregated Tables ---

def load_summary_by_user():
    """Loads user-level summary for KPI/leaderboard use."""
    fpath = os.path.join(DATA_DIR, "summary_by_user.csv")
    return pd.read_csv(fpath)

def load_summary_by_department():
    """Loads department-level summary."""
    fpath = os.path.join(DATA_DIR, "summary_by_department.csv")
    return pd.read_csv(fpath)

def load_summary_by_category():
    """Loads category-level summary."""
    fpath = os.path.join(DATA_DIR, "summary_by_category.csv")
    return pd.read_csv(fpath)

def load_summary_attachments_by_user():
    """Loads attachment summary per user/department."""
    fpath = os.path.join(DATA_DIR, "summary_attachments_by_user.csv")
    return pd.read_csv(fpath)

def load_health_metrics():
    """Loads CSV with key data health/quality metrics for display in dashboard."""
    fpath = os.path.join(DATA_DIR, "data_health.csv")
    s = pd.read_csv(fpath, index_col=0, header=None)
    s = s.squeeze("columns")  # Convert to Series if possible
    return s.to_dict()

# --- Unified Loader for Dashboard App ---

def load_all_data():
    """Convenience loader for dashboard: returns all primary tables."""
    schemes = load_schemes()
    workflow = load_workflow()
    attachments = load_attachments()
    summary_user = load_summary_by_user()
    summary_dept = load_summary_by_department()
    summary_cat = load_summary_by_category()
    summary_attach_user = load_summary_attachments_by_user()
    health_metrics = load_health_metrics()
    return {
        "schemes": schemes,
        "workflow": workflow,
        "attachments": attachments,
        "summary_by_user": summary_user,
        "summary_by_department": summary_dept,
        "summary_by_category": summary_cat,
        "summary_attachments_by_user": summary_attach_user,
        "data_health": health_metrics
    }

# --- Usage Example (for testing or dev) ---
if __name__ == "__main__":
    data = load_all_data()
    
    for k, v in data.items():
        print(f"{k}: {type(v)} rows={len(v) if hasattr(v,'__len__') else '-'}")
