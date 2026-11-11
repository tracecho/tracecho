"""
Benchmark replacement-candidate search script.
Searches both RBI and SEBI parquet chunk stores for the best alternative chunks for each audited question.
READ-ONLY — no files modified except output JSON.
"""
import pandas as pd
import json
import re
import sys
from collections import defaultdict

base = r'd:\REGINTEL-20260820T084445Z-1-001\REGINTEL\regintel\data\processed'

sys.stdout.write("Loading parquets...\n"); sys.stdout.flush()
rdf = pd.read_parquet(base + r'\rbi_chunks.parquet')
sdf = pd.read_parquet(base + r'\sebi_chunks.parquet')
sys.stdout.write(f"RBI: {rdf.shape}, SEBI: {sdf.shape}\n"); sys.stdout.flush()
sys.stdout.write(f"RBI cols: {list(rdf.columns)}\n")
sys.stdout.write(f"SEBI cols: {list(sdf.columns)}\n")
sys.stdout.flush()

# Normalize text column
rdf['_text'] = rdf['text'].fillna('').astype(str).str.lower()
sdf['_text'] = sdf['text'].fillna('').astype(str).str.lower()

def search(df, keywords, must_have=None, exclude=None, top_n=5, id_col='chunk_id', date_col='issue_date', title_col='subject'):
    """Score rows by keyword hit count and return top_n."""
    scores = pd.Series(0, index=df.index)
    for kw in keywords:
        hits = df['_text'].str.contains(re.escape(kw.lower()), regex=False)
        scores += hits.astype(int)
    if must_have:
        mask = pd.Series(True, index=df.index)
        for kw in must_have:
            mask &= df['_text'].str.contains(re.escape(kw.lower()), regex=False)
        scores[~mask] = 0
    if exclude:
        for kw in exclude:
            bad = df['_text'].str.contains(re.escape(kw.lower()), regex=False)
            scores[bad] = 0
    top = scores.nlargest(top_n)
    top = top[top > 0]
    results = []
    for idx, score in top.items():
        row = df.loc[idx]
        snippet = str(row['text'])[:400]
        results.append({
            'chunk_id': str(row.get(id_col, '') or row.get('chunk_id', '')),
            'doc_id': str(row.get('document_id', '')),
            'regulator': str(row.get('regulator', '')),
            'date': str(row.get(date_col, '') or row.get('date', 'N/A')),
            'subject': str(row.get(title_col, '') or row.get('title', 'N/A'))[:120],
            'score': int(score),
            'snippet': snippet,
        })
    return results

# ────────────────────────────────────────────────────────────────────────────
# PER-QUESTION SEARCHES
# ────────────────────────────────────────────────────────────────────────────

questions = {}

# q_007: Grievance redressal mechanism for MUTUAL FUNDS — want SEBI
sys.stdout.write("q_007...\n"); sys.stdout.flush()
questions['q_007'] = {
    'q': "What are the guidelines on grievance redressal mechanisms for mutual funds?",
    'want_regulator': 'SEBI', 'temporal_type': 'CURRENT',
    'rbi': search(rdf, ['grievance', 'mutual fund', 'redressal'], must_have=['grievance']),
    'sebi': search(sdf, ['grievance', 'mutual fund', 'redressal', 'investor grievance'], must_have=['grievance']),
}

# q_009: IPO disclosure requirements — want SEBI
sys.stdout.write("q_009...\n"); sys.stdout.flush()
questions['q_009'] = {
    'q': "What are the disclosure requirements for a company launching an IPO?",
    'want_regulator': 'SEBI', 'temporal_type': 'CURRENT',
    'rbi': search(rdf, ['ipo', 'initial public offer', 'prospectus', 'disclosure', 'icdr']),
    'sebi': search(sdf, ['ipo', 'initial public offer', 'prospectus', 'disclosure requirement', 'icdr', 'public issue'],
                   must_have=['disclosure']),
}

# q_010: Role of debenture trustee — partial match existing, find better
sys.stdout.write("q_010...\n"); sys.stdout.flush()
questions['q_010'] = {
    'q': "What is the role of a debenture trustee?",
    'want_regulator': 'SEBI', 'temporal_type': 'CURRENT',
    'rbi': search(rdf, ['debenture trustee', 'roles', 'responsibilities', 'obligation'], must_have=['debenture trustee']),
    'sebi': search(sdf, ['debenture trustee', 'roles', 'responsibilities', 'duties', 'obligation'], must_have=['debenture trustee']),
}

# q_012: Margin requirements for derivatives — want SEBI exchange context
sys.stdout.write("q_012...\n"); sys.stdout.flush()
questions['q_012'] = {
    'q': "What are the margin requirements for derivatives trading?",
    'want_regulator': 'SEBI', 'temporal_type': 'CURRENT',
    'rbi': search(rdf, ['margin requirement', 'derivative', 'futures', 'options', 'initial margin', 'exposure margin']),
    'sebi': search(sdf, ['margin', 'derivative', 'futures', 'options', 'initial margin', 'exposure margin', 'span', 'clearing corporation'],
                   must_have=['margin']),
}

# q_016: Related party transactions (RPT) — want SEBI listed entity rules
sys.stdout.write("q_016...\n"); sys.stdout.flush()
questions['q_016'] = {
    'q': "What are the rules regarding related party transactions?",
    'want_regulator': 'SEBI', 'temporal_type': 'CURRENT',
    'rbi': search(rdf, ['related party', 'related party transaction', 'arm\'s length', 'approval of shareholders']),
    'sebi': search(sdf, ['related party', 'related party transaction', 'arm\'s length', 'materiality', 'lodr', 'listed',
                         'audit committee approval'], must_have=['related party']),
}

# q_026: Margin trading HISTORICAL 2020-2022 (question says 2021)
sys.stdout.write("q_026...\n"); sys.stdout.flush()
questions['q_026'] = {
    'q': "What were the margin trading rules in 2021?",
    'want_regulator': 'SEBI', 'temporal_type': 'HISTORICAL', 'temporal_window': '2020-2022',
    'rbi': search(rdf, ['margin trading', 'margin trading facility', 'mtf', '2021', '2020']),
    'sebi': search(sdf, ['margin trading', 'margin trading facility', 'mtf', 'pledging', 'approved securities'],
                   must_have=['margin trading']),
}

# q_029: Independent directors guidelines HISTORICAL pre-2022 (SEBI)
sys.stdout.write("q_029...\n"); sys.stdout.flush()
questions['q_029'] = {
    'q': "What were the guidelines for independent directors before 2022?",
    'want_regulator': 'SEBI', 'temporal_type': 'HISTORICAL', 'temporal_window': '2020-2022',
    'rbi': search(rdf, ['independent director', 'nomination committee', 'tenure', 'pecuniary relationship']),
    'sebi': search(sdf, ['independent director', 'lodr', 'nomination', 'pecuniary', 'tenure', 'listing obligation'],
                   must_have=['independent director']),
}

# q_030: Payment aggregators HISTORICAL 2019 (window 2020-2022)
sys.stdout.write("q_030...\n"); sys.stdout.flush()
questions['q_030'] = {
    'q': "How were payment aggregators regulated in 2019?",
    'want_regulator': 'RBI', 'temporal_type': 'HISTORICAL', 'temporal_window': '2020-2022',
    'rbi': search(rdf, ['payment aggregator', 'payment gateway', 'dpss', 'online payment', 'pa-pg', '2020', '2021'],
                  must_have=['payment aggregator']),
    'sebi': search(sdf, ['payment aggregator', 'payment gateway'], must_have=['payment aggregator']),
}

# q_031: MF disclosure requirements HISTORICAL 2018 (window 2020-2022)
sys.stdout.write("q_031...\n"); sys.stdout.flush()
questions['q_031'] = {
    'q': "What were the disclosure requirements for mutual funds in 2018?",
    'want_regulator': 'SEBI', 'temporal_type': 'HISTORICAL', 'temporal_window': '2020-2022',
    'rbi': search(rdf, ['mutual fund', 'disclosure', 'scheme information', 'amfi', 'fact sheet']),
    'sebi': search(sdf, ['mutual fund', 'disclosure', 'scheme information document', 'fact sheet', 'amfi', '2018'],
                   must_have=['disclosure']),
}

# q_033: Startup exemptions for mandatory disclosures (SEBI)
sys.stdout.write("q_033...\n"); sys.stdout.flush()
questions['q_033'] = {
    'q': "Are there exemptions for startups regarding mandatory disclosures?",
    'want_regulator': 'SEBI', 'temporal_type': 'CURRENT',
    'rbi': search(rdf, ['startup', 'exemption', 'disclosure', 'innovators', 'igp', 'sme']),
    'sebi': search(sdf, ['startup', 'exemption', 'disclosure', 'innovators growth platform', 'igp', 'sme', 'emerge'],
                   must_have=['startup']),
}

# q_035: Trading limits relaxed for a broker (SEBI)
sys.stdout.write("q_035...\n"); sys.stdout.flush()
questions['q_035'] = {
    'q': "In what cases can trading limits be relaxed for a broker?",
    'want_regulator': 'SEBI', 'temporal_type': 'CURRENT',
    'rbi': search(rdf, ['trading limit', 'broker', 'exposure limit', 'position limit', 'relaxation']),
    'sebi': search(sdf, ['trading limit', 'broker', 'exposure limit', 'position limit', 'relaxation', 'stock broker',
                         'risk management'], must_have=['broker']),
}

# q_036: Exceptions to lock-in for anchor investors (SEBI)
sys.stdout.write("q_036...\n"); sys.stdout.flush()
questions['q_036'] = {
    'q': "What are the exceptions to the lock-in period for anchor investors?",
    'want_regulator': 'SEBI', 'temporal_type': 'CURRENT',
    'rbi': search(rdf, ['anchor investor', 'lock-in', 'lock in period', 'ipo', 'icdr']),
    'sebi': search(sdf, ['anchor investor', 'lock-in', 'lock in period', 'lock in', 'allocation', 'icdr'],
                   must_have=['anchor']),
}

# q_045: SEBI vs RBI on foreign investment limits (cross-reg — need BOTH)
sys.stdout.write("q_045...\n"); sys.stdout.flush()
questions['q_045'] = {
    'q': "How do SEBI and RBI differ on foreign investment limits?",
    'want_regulator': 'BOTH', 'temporal_type': 'CURRENT',
    'rbi': search(rdf, ['foreign investment', 'fpi', 'fdi', 'investment limit', 'sectoral limit', 'aggregate limit'],
                  must_have=['foreign']),
    'sebi': search(sdf, ['foreign investment', 'fpi', 'fdi', 'investment limit', 'sectoral limit', 'aggregate limit'],
                   must_have=['foreign']),
}

# q_046: Joint cybersecurity reporting for banks acting as brokers (cross-reg)
sys.stdout.write("q_046...\n"); sys.stdout.flush()
questions['q_046'] = {
    'q': "What are the joint cybersecurity reporting requirements for banks acting as brokers?",
    'want_regulator': 'BOTH', 'temporal_type': 'CURRENT',
    'rbi': search(rdf, ['cybersecurity', 'cyber security', 'reporting', 'broker', 'sebi', 'incident report'],
                  must_have=['cyber']),
    'sebi': search(sdf, ['cybersecurity', 'cyber security', 'reporting', 'bank', 'broker', 'incident'],
                   must_have=['cyber']),
}

# ────────────────────────────────────────────────────────────────────────────
# OUTPUT RESULTS
# ────────────────────────────────────────────────────────────────────────────

out_file = r'd:\REGINTEL-20260820T084445Z-1-001\replacement_candidates.json'
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(questions, f, indent=2, ensure_ascii=False)
sys.stdout.write(f"\nSaved to {out_file}\n")

# Print summary
for qid, data in questions.items():
    sys.stdout.write(f"\n{'='*60}\n{qid}: {data['q']}\n")
    sys.stdout.write(f"  Want regulator: {data.get('want_regulator')} | Temporal: {data.get('temporal_type')}\n")
    rbi_hits = data.get('rbi', [])
    sebi_hits = data.get('sebi', [])
    sys.stdout.write(f"  RBI hits: {len(rbi_hits)}, SEBI hits: {len(sebi_hits)}\n")
    for src, hits in [('RBI', rbi_hits[:2]), ('SEBI', sebi_hits[:2])]:
        for h in hits:
            sys.stdout.write(f"  [{src}] score={h['score']} id={h['chunk_id']}\n")
            sys.stdout.write(f"        date={h['date']} subject={h['subject'][:80]}\n")
            sys.stdout.write(f"        snippet: {h['snippet'][:200]}\n")
sys.stdout.flush()
