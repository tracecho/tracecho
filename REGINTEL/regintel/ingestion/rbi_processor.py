import os
import re
import pandas as pd
import glob

def process_rbi_texts(input_dir, output_file):
    txt_files = glob.glob(os.path.join(input_dir, '*.txt'))
    print(f"Found {len(txt_files)} RBI text files.")
    
    all_chunks = []
    
    for filepath in txt_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Basic cleanup
        content = re.sub(r'\[PAGE \d+\]', '', content)
        
        # Heuristic Metadata Extraction
        circular_match = re.search(r'(RBI/\d{4}-\d{2,4}/\d+)', content)
        circular_number = circular_match.group(1) if circular_match else "UNKNOWN"
        
        date_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', content)
        issue_date = date_match.group(1) if date_match else "UNKNOWN"
        
        # Just taking first few lines as subject for now
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        subject = next((line for line in lines if "Master Circular" in line or "Master Direction" in line), "UNKNOWN")
        if subject == "UNKNOWN" and len(lines) > 5:
            subject = lines[5] # fallback
            
        paras = content.split('\n\n')
        
        for i, p in enumerate(paras):
            p = re.sub(r'\s+', ' ', p).strip()
            if len(p) < 30: continue
            
            chunk = {
                'chunk_id': f"RBI-{os.path.basename(filepath)}-{i}",
                'document_id': os.path.basename(filepath),
                'regulator': 'RBI',
                'document_type': 'Circular' if 'Circular' in subject else 'Master Direction' if 'Direction' in subject else 'Notification',
                'circular_number': circular_number,
                'issue_date': issue_date,
                'subject': subject,
                'validity_status': 'unknown',
                'text': p
            }
            all_chunks.append(chunk)

    chunk_df = pd.DataFrame(all_chunks)
    print(f"Generated {len(chunk_df)} RBI chunks.")
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    chunk_df.to_parquet(output_file)
    print(f"Saved RBI chunks to {output_file}")

if __name__ == '__main__':
    input_dir = r"D:\REGINTEL\RegIntel-20260819T115643Z-1-001\RegIntel\text\RBI"
    output_file = r"D:\REGINTEL\regintel\data\processed\rbi_chunks.parquet"
    process_rbi_texts(input_dir, output_file)
