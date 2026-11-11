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

sys.stdout.write("Loading RBI parquet...\n")
sys.stdout.flush()
rdf = pd.read_parquet(base + r'\rbi_chunks.parquet')
sys.stdout.write(f"RBI cols: {list(rdf.columns)}\n")
sys.stdout.write(f"RBI shape: {rdf.shape}\n")
sys.stdout.flush()

sys.stdout.write("Loading SEBI parquet...\n")
sys.stdout.flush()
sdf = pd.read_parquet(base + r'\sebi_chunks.parquet')
sys.stdout.write(f"SEBI cols: {list(sdf.columns)}\n")
sys.stdout.write(f"SEBI shape: {sdf.shape}\n")
sys.stdout.flush()

# Find ID column
def find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

rbi_id_col = find_col(rdf, ['chunk_id', 'id', 'chunk_id_full'])
sebi_id_col = find_col(sdf, ['chunk_id', 'id', 'chunk_id_full'])
rbi_text_col = find_col(rdf, ['text', 'content', 'chunk_text', 'passage'])
sebi_text_col = find_col(sdf, ['text', 'content', 'chunk_text', 'passage'])
rbi_date_col = find_col(rdf, ['doc_date', 'date', 'issue_date', 'circular_date'])
sebi_date_col = find_col(sdf, ['doc_date', 'date', 'issue_date', 'circular_date'])
rbi_title_col = find_col(rdf, ['title', 'document_title', 'doc_title', 'subject'])
sebi_title_col = find_col(sdf, ['title', 'document_title', 'doc_title', 'subject'])

sys.stdout.write(f"RBI id_col={rbi_id_col}, text_col={rbi_text_col}, date_col={rbi_date_col}, title_col={rbi_title_col}\n")
sys.stdout.write(f"SEBI id_col={sebi_id_col}, text_col={sebi_text_col}, date_col={sebi_date_col}, title_col={sebi_title_col}\n")
sys.stdout.flush()

results = {}

for q, chunk_id in rbi_targets.items():
    if not rbi_id_col:
        results[q] = {'chunk_id': chunk_id, 'found': False, 'error': 'no id col'}
        continue
    rows = rdf[rdf[rbi_id_col] == chunk_id]
    if len(rows) == 0:
        results[q] = {'chunk_id': chunk_id, 'found': False}
    else:
        row = rows.iloc[0]
        results[q] = {
            'chunk_id': chunk_id,
            'found': True,
            'text': str(row[rbi_text_col])[:3000] if rbi_text_col else 'N/A',
            'doc_date': str(row[rbi_date_col]) if rbi_date_col else 'N/A',
            'doc_title': str(row[rbi_title_col]) if rbi_title_col else 'N/A',
        }

for q, chunk_id in sebi_targets.items():
    if not sebi_id_col:
        results[q] = {'chunk_id': chunk_id, 'found': False, 'error': 'no id col'}
        continue
    rows = sdf[sdf[sebi_id_col] == chunk_id]
    if len(rows) == 0:
        results[q] = {'chunk_id': chunk_id, 'found': False}
    else:
        row = rows.iloc[0]
        results[q] = {
            'chunk_id': chunk_id,
            'found': True,
            'text': str(row[sebi_text_col])[:3000] if sebi_text_col else 'N/A',
            'doc_date': str(row[sebi_date_col]) if sebi_date_col else 'N/A',
            'doc_title': str(row[sebi_title_col]) if sebi_title_col else 'N/A',
        }

out_file = r'd:\REGINTEL-20260820T084445Z-1-001\chunk_audit_results.json'
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
sys.stdout.write(f"Saved results to {out_file}\n")

# Print summary
for q, info in sorted(results.items()):
    sys.stdout.write(f"\n=== {q} === chunk: {info['chunk_id']}\n")
    sys.stdout.write(f"  found: {info.get('found')}\n")
    if info.get('found'):
        sys.stdout.write(f"  date: {info.get('doc_date')}\n")
        sys.stdout.write(f"  title: {info.get('doc_title')}\n")
        sys.stdout.write(f"  text[:400]: {info.get('text','')[:400]}\n")
    sys.stdout.flush()
