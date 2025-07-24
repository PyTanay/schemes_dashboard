import pandas as pd
import numpy as np
import os

# Adjust output directory as per your requirements
OUTDIR = r"D:\Automation\python\schemes_dashboard\data"

# 1. Load Data
def load_csvs(data_dir=OUTDIR):
    schemes = pd.read_csv(
        os.path.join(data_dir, "schemes.csv"),
        parse_dates=["creationDate"],
        dayfirst=True, infer_datetime_format=True,
        dtype=str
    )
    workflow = pd.read_csv(
        os.path.join(data_dir, "workflow.csv"),
        parse_dates=["forwarded_at"],
        dayfirst=True, infer_datetime_format=True,
        dtype=str
    )
    attachments = pd.read_csv(
        os.path.join(data_dir, "attachments.csv"),
        dtype=str
    )
    return schemes, workflow, attachments

# 2. Data Audit & Health Checks
def audit_data(schemes, workflow, attachments):
    health = {}
    # Ensure correct types
    # print(schemes)
    schemes['creationDate'] = pd.to_datetime(schemes['creationDate'], errors='coerce')
    workflow['forwarded_at'] = pd.to_datetime(workflow['forwarded_at'], errors='coerce')
    # Health checks
    health['schemes_missing_scheme_id'] = schemes['scheme_id'].isnull().sum()
    health['schemes_missing_creationDate'] = schemes['creationDate'].isnull().sum()
    health['schemes_missing_category'] = schemes['category'].isnull().sum()
    health['schemes_missing_department'] = schemes['department_at_time'].isnull().sum()
    health['workflow_missing_scheme_id'] = workflow['scheme_id'].isnull().sum()
    health['workflow_missing_forwarded_at'] = workflow['forwarded_at'].isnull().sum()
    health['workflow_missing_time_taken'] = workflow['time_taken'].isnull().sum() if 'time_taken' in workflow.columns else np.nan
    health['attachments_missing_scheme_id'] = attachments['scheme_id'].isnull().sum()
    health['attachments_missing_fileName'] = attachments['fileName'].isnull().sum()
    # Duplicates
    health['schemes_duplicate_scheme_id'] = schemes['scheme_id'].duplicated().sum()
    health['workflow_duplicate_rows'] = workflow.duplicated().sum()
    health['attachments_duplicate_rows'] = attachments.duplicated().sum()
    # Proper aging using last workflow date
    last_forw = workflow.groupby('scheme_id')['forwarded_at'].max().reset_index()
    last_forw.rename(columns={'forwarded_at': 'last_action_date'}, inplace=True)
    merged = schemes.merge(last_forw, on='scheme_id', how='left')
    merged['aging_days'] = (merged['last_action_date'] - merged['creationDate']).dt.days
    health['schemes_aging_gt_180'] = merged['aging_days'].dropna().gt(180).sum()
    return health

# 3. Clean and Enrich Data
def clean_and_enrich(schemes, workflow, attachments):
    # Remove rows without essential keys
    schemes = schemes.dropna(subset=['scheme_id', 'creationDate'])
    # Type conversions
    schemes['creationDate'] = pd.to_datetime(schemes['creationDate'], errors='coerce')
    workflow = workflow.dropna(subset=['scheme_id', 'forwarded_at'])
    workflow['forwarded_at'] = pd.to_datetime(workflow['forwarded_at'], errors='coerce')
    if 'time_taken' in workflow.columns:
        workflow['time_taken'] = pd.to_numeric(workflow['time_taken'], errors='coerce')

    # Compute last comment/action per scheme
    last_forw = workflow.groupby('scheme_id')['forwarded_at'].max().reset_index()
    last_forw.rename(columns={'forwarded_at': 'last_action_date'}, inplace=True)
    schemes = schemes.merge(last_forw, on='scheme_id', how='left')

    # Aging calculation: last_action_date - creationDate
    schemes['aging_days'] = (schemes['last_action_date'] - schemes['creationDate']).dt.days
    # Assign bucket based on aging_days
    schemes['aging_bucket'] = pd.cut(
        schemes['aging_days'],
        bins=[-1, 90, 180, float('inf')],
        labels=["< 90 days", "90–180 days", "> 180 days"]
    )

    # Normalize categorical columns
    for col in ['department_at_time', 'plant', 'category']:
        if col in schemes:
            schemes[col] = schemes[col].astype(str).str.strip().str.upper().replace('NAN', np.nan).fillna("UNKNOWN")
    attachments = attachments.dropna(subset=['scheme_id', 'fileName'])
    return schemes, workflow, attachments

# 4. Pre-Aggregation & Summary Tables
def generate_summary_tables(schemes, workflow, attachments, outdir=OUTDIR):
    # By User
    if not workflow.empty:
        by_user = workflow.groupby(['user', 'department'])['scheme_id'].nunique().reset_index()
        by_user.rename(columns={'scheme_id': 'schemes_handled'}, inplace=True)
        if 'time_taken' in workflow.columns:
            by_user['avg_processing_time'] = workflow.groupby(['user', 'department'])['time_taken'].mean().values
        by_user.to_csv(os.path.join(outdir, "summary_by_user.csv"), index=False)
    # By Department
    if not schemes.empty:
        by_dept = schemes.groupby('department_at_time')['scheme_id'].nunique().reset_index()
        by_dept.rename(columns={'scheme_id': 'schemes_handled'}, inplace=True)
        by_dept.to_csv(os.path.join(outdir, "summary_by_department.csv"), index=False)
        by_cat = schemes.groupby('category')['scheme_id'].nunique().reset_index()
        by_cat.rename(columns={'scheme_id': 'schemes_handled'}, inplace=True)
        by_cat.to_csv(os.path.join(outdir, "summary_by_category.csv"), index=False)
    # Attachments by User
    if not attachments.empty:
        by_user_attach = attachments.groupby(['user', 'department'])['fileName'].count().reset_index()
        by_user_attach.rename(columns={'fileName': 'total_attachments'}, inplace=True)
        by_user_attach.to_csv(os.path.join(outdir, "summary_attachments_by_user.csv"), index=False)

# 5. Save Cleaned Data
def save_clean_data(schemes, workflow, attachments, outdir=OUTDIR):
    schemes.to_csv(os.path.join(outdir, "schemes_cleaned.csv"), index=False)
    workflow.to_csv(os.path.join(outdir, "workflow_cleaned.csv"), index=False)
    attachments.to_csv(os.path.join(outdir, "attachments_cleaned.csv"), index=False)

# 6. Health Check Save
def save_health_summary(data_health, outdir=OUTDIR):
    pd.Series(data_health).to_csv(os.path.join(outdir, "data_health.csv"))

# 7. Main Routine
def main():
    print(f"Loading data from {OUTDIR} ...")
    schemes, workflow, attachments = load_csvs()
    print("Auditing data...")
    data_health = audit_data(schemes, workflow, attachments)
    print("Cleaning and enriching...")
    schemes_clean, workflow_clean, attachments_clean = clean_and_enrich(schemes, workflow, attachments)
    print("Saving cleaned data...")
    save_clean_data(schemes_clean, workflow_clean, attachments_clean)
    print("Generating summary tables...")
    generate_summary_tables(schemes_clean, workflow_clean, attachments_clean)
    print("Saving health summary...")
    save_health_summary(data_health)
    print("Preprocessing complete. Outputs saved in:", OUTDIR)

if __name__ == "__main__":
    main()
