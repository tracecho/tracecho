import pandas as pd
import json
import sys

rbi_targets = {
    'q_007': 'RBI-RBI_0382.txt-6',
    'q_009': 'RBI-RBI_0012.txt-154',
    'q_010': 'RBI-RBI_0429.txt-11',
    'q_012': 'RBI-RBI_0071.txt-19',
    'q_016': 'RBI-RBI_0231.txt-34',
    'q_029': 'RBI-RBI_0098.txt-5',
    'q_030': 'RBI-RBI_0444.txt-0',
    'q_033': 'RBI-RBI_0092.txt-49',
    'q_035': 'RBI-RBI_0142.txt-94',
    'q_036': 'RBI-RBI_0177.txt-18',
    'q_046': 'RBI-RBI_0409.txt-47',
}
sebi_targets = {
    'q_026': 'SEBI-SEBI/HO/MRD/MRD-PoD-2/P/CIR/2025/120-0',
    'q_031': 'SEBI-SEBI/HO/IMD/PoD1/CIR/P/2024/150-0',
    'q_045': 'SEBI-SEBI/HO/AFD/AFD-POD-3/P/CIR/2024/152-0',
}

base = r'd:\REGINTEL-20260820T084445Z-1-001\REGINTEL\regintel\data\processed'
rdf = pd.read_parquet(base + r'\rbi_chunks.parquet')
sdf = pd.read_parquet(base + r'\sebi_chunks.parquet')

def find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

rbi_id_col = find_col(rdf, ['chunk_id', 'id'])
sebi_id_col = find_col(sdf, ['chunk_id', 'id'])
rbi_text_col = find_col(rdf, ['text', 'content', 'chunk_text'])
sebi_text_col = find_col(sdf, ['text', 'content', 'chunk_text'])

results = {}

for q, chunk_id in rbi_targets.items():
    rows = rdf[rdf[rbi_id_col] == chunk_id]
    if len(rows) == 0:
        results[q] = {'chunk_id': chunk_id, 'found': False}
    else:
        row = rows.iloc[0]
        results[q] = {
            'chunk_id': chunk_id,
            'found': True,
            'text': str(row[rbi_text_col]) if rbi_text_col else 'N/A',
            'doc_date': str(row.get('date', row.get('doc_date', 'N/A'))),
            'doc_title': str(row.get('title', row.get('doc_title', 'N/A'))),
            'doc_id': str(row.get('doc_id', 'N/A')),
            'all_cols': {c: str(row[c])[:200] for c in rdf.columns},
        }

for q, chunk_id in sebi_targets.items():
    rows = sdf[sdf[sebi_id_col] == chunk_id]
    if len(rows) == 0:
        results[q] = {'chunk_id': chunk_id, 'found': False}
    else:
        row = rows.iloc[0]
        results[q] = {
            'chunk_id': chunk_id,
            'found': True,
            'text': str(row[sebi_text_col]) if sebi_text_col else 'N/A',
            'doc_date': str(row.get('date', row.get('doc_date', 'N/A'))),
            'doc_title': str(row.get('title', row.get('doc_title', 'N/A'))),
            'doc_id': str(row.get('doc_id', 'N/A')),
            'all_cols': {c: str(row[c])[:200] for c in sdf.columns},
        }

out_file = r'd:\REGINTEL-20260820T084445Z-1-001\chunk_audit_full.json'
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
sys.stdout.write(f"Saved {len(results)} results to {out_file}\n")
sys.stdout.flush()
