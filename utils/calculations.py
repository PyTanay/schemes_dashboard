import pandas as pd

def average_processing_time(workflow_df):
    return (
        workflow_df.groupby(['user', 'department'])['time_taken']
        .mean()
        .reset_index()
        .rename(columns={"time_taken": "avg_processing_time"})
    )

def average_attachments_per_user(attachments_df):
    return (
        attachments_df.groupby(['user', 'department'])['fileName']
        .count()
        .reset_index()
        .rename(columns={"fileName": "total_attachments"})
    )

def aging_buckets(schemes_df, cutoff_date):
    age = (cutoff_date - schemes_df["creationDate"]).dt.days
    return pd.cut(
        age,
        bins=[-1, 90, 180, float('inf')],
        labels=["< 90 days", "90–180 days", "> 180 days"]
    )

def determine_pending_owners(workflow_df, as_of_date):
    filtered = workflow_df[workflow_df["forwarded_at"] <= as_of_date]
    latest_step = filtered.sort_values("forwarded_at").groupby("scheme_id").tail(1)
    return latest_step[["scheme_id", "user", "department", "forwarded_at"]]

def classify_aging_buckets(schemes_df, workflow_df, end_date):
    # Find the latest owner as of end_date
    latest = workflow_df[workflow_df["forwarded_at"] <= end_date]
    latest = latest.sort_values("forwarded_at").groupby("scheme_id").tail(1)

    # Merge with schemes to get creation date
    pending = latest.merge(schemes_df[["scheme_id", "creationDate"]], on="scheme_id", how="left")
    pending["aging_days"] = (end_date - pending["creationDate"]).dt.days

    # Bucket classification
    pending["aging_bucket"] = pd.cut(
        pending["aging_days"],
        bins=[-1, 90, 180, float('inf')],
        labels=["< 90 days", "90–180 days", "> 180 days"]
    )

    return pending
