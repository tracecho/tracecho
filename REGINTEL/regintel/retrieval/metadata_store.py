import pandas as pd
import json
import os

class MetadataStore:
    def __init__(self, metadata_path=r"D:\REGINTEL-20260820T084445Z-1-001\REGINTEL\regintel\data\processed\metadata.json"):
        self.metadata_path = metadata_path
        self.metadata = {}

    def build_store(self, sebi_path="d:/REGINTEL/regintel/data/processed/sebi_chunks.parquet", 
                          rbi_path="d:/REGINTEL/regintel/data/processed/rbi_chunks.parquet"):
        sebi_df = pd.read_parquet(sebi_path)
        rbi_df = pd.read_parquet(rbi_path)
        df = pd.concat([sebi_df, rbi_df], ignore_index=True)
        
        # Select columns to store
        cols = ['chunk_id', 'document_id', 'regulator', 'subject', 'document_type', 
                'section', 'paragraph', 'issue_date', 'effective_date', 
                'validity_status', 'source_url', 'text', 'document_origin']
        
        # Missing columns can exist
        actual_cols = [c for c in cols if c in df.columns]
        
        self.metadata = df.set_index('chunk_id')[[c for c in actual_cols if c != 'chunk_id']].to_dict(orient='index')
        
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f)
            
    def load(self):
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            return True
        return False

    def get(self, chunk_id):
        row = self.metadata.get(chunk_id, {})
        if row and 'subject' in row:
            import re
            subj = str(row['subject'])
            subj = re.sub(r"(?i)\b(validity|section|issue_date|source_url|chunk_id|regulator)\b.*$", "", subj)
            row['subject'] = subj.strip(" \t\n\r|,-=")
        return row
