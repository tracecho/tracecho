import pandas as pd
import json
import random
import os

def generate_golden_queries():
    out_file = r"d:\REGINTEL\regintel\evaluation\golden_queries.json"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    
    sebi_df = pd.read_parquet(r"d:\REGINTEL\regintel\data\processed\sebi_chunks.parquet")
    rbi_df = pd.read_parquet(r"d:\REGINTEL\regintel\data\processed\rbi_chunks.parquet")
    
    # We will pick a simple heuristic to generate queries from the chunk text
    queries = {}
    
    # helper
    def add_queries(df, num, prefix):
        # sample 'num' random rows
        sampled = df.sample(num, random_state=42)
        for _, row in sampled.iterrows():
            cid = row['chunk_id']
            text = row['text']
            subject = row.get('subject', 'General')
            
            # extract some words as a fake query for testing
            words = text.split()
            if len(words) > 10:
                # pick some words near the beginning maybe
                q = f"What does the {prefix} regulation say about {' '.join(words[5:10])}?"
            else:
                q = f"What is {subject} in {prefix}?"
            
            # create a test question
            # For a more realistic test, we can just use the exact sequence of 5 words
            queries[q] = [cid]
            
    add_queries(sebi_df, 25, "SEBI")
    add_queries(rbi_df, 25, "RBI")
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(queries, f, indent=4)
        
    print(f"Generated {len(queries)} golden queries to {out_file}")

if __name__ == '__main__':
    generate_golden_queries()
