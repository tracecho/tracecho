import pandas as pd
import re
import uuid
import os

def clean_text(text):
    if not isinstance(text, str): return ""
    text = re.sub(r'\[PAGE \d+\]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def chunk_sebi(row):
    text = clean_text(row.get('text', ''))
    chunks = []
    # simple chunking by paragraphs for illustration
    paras = text.split('\n\n')
    
    for i, p in enumerate(paras):
        if len(p.strip()) < 20: continue
        chunk = {
            'chunk_id': f"SEBI-{row.get('circular_number', 'UNKN')}-{i}",
            'document_id': row.get('circular_number', 'UNKN'),
            'regulator': 'SEBI',
            'document_type': row.get('circular_type', 'Circular'),
            'subject': row.get('subject', ''),
            'validity_status': row.get('validity_status', 'unknown'),
            'text': p.strip()
        }
        chunks.append(chunk)
    return chunks

def process():
    in_file = r"D:\REGINTEL\RegIntel-20260819T115643Z-1-001\RegIntel\SEBI\sebi_corpus.parquet"
    out_file = r"D:\REGINTEL\regintel\data\processed\sebi_chunks.parquet"
    print(f"Loading {in_file}")
    df = pd.read_parquet(in_file)
    print(f"Loaded {len(df)} SEBI documents.")
    
    all_chunks = []
    for _, row in df.iterrows():
        all_chunks.extend(chunk_sebi(row))
        
    chunk_df = pd.DataFrame(all_chunks)
    print(f"Generated {len(chunk_df)} SEBI chunks.")
    
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    chunk_df.to_parquet(out_file)
    print(f"Saved chunks to {out_file}")

if __name__ == '__main__':
    process()
