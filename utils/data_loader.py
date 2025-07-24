import pandas as pd

def load_data():
    schemes = pd.read_csv("data/schemes.csv", parse_dates=["creationDate"])
    workflow = pd.read_csv("data/workflow.csv", parse_dates=["forwarded_at"])
    attachments = pd.read_csv("data/attachments.csv")

    # Merge on scheme_id
    merged = schemes.merge(workflow, on="scheme_id", how="left", suffixes=("", "_workflow"))
    merged = merged.merge(attachments, on="scheme_id", how="left", suffixes=("", "_attachment"))

    return schemes, workflow, attachments, merged
def load_schemes():
    return pd.read_csv("data/schemes.csv")