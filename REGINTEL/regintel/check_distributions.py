import pandas as pd

def check_distributions():
    print("Checking SEBI Metadata Distributions...")
    sebi_df = pd.read_parquet(r"d:\REGINTEL\regintel\data\processed\sebi_chunks.parquet")
    cols = ['validity_status', 'effective_date', 'superseded_by_id', 'version_lineage', 'supersession_edges']
    for col in cols:
        if col in sebi_df.columns:
            print(f"\n--- SEBI: {col} ---")
            print(sebi_df[col].value_counts(dropna=False).head(10))
        else:
            print(f"\n--- SEBI: {col} --- Not found in columns.")

    print("\n\nChecking RBI Metadata Distributions...")
    rbi_df = pd.read_parquet(r"d:\REGINTEL\regintel\data\processed\rbi_chunks.parquet")
    for col in cols:
        if col in rbi_df.columns:
            print(f"\n--- RBI: {col} ---")
            print(rbi_df[col].value_counts(dropna=False).head(10))
        else:
            print(f"\n--- RBI: {col} --- Not found in columns.")

if __name__ == '__main__':
    check_distributions()
