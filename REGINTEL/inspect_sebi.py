import pandas as pd

try:
    df = pd.read_parquet(r"D:\REGINTEL\RegIntel-20260819T115643Z-1-001\RegIntel\SEBI\sebi_corpus.parquet")
    print("SEBI Corpus Details:")
    print("Columns:", df.columns.tolist())
    print("\nHead (1 row):")
    print(df.head(1).to_dict(orient='records'))
    print("\nValue counts for validity_status:")
    print(df['validity_status'].value_counts())
except Exception as e:
    print(f"Error reading SEBI parquet: {e}")
