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
        circular_number = circular_match.group(1) if circular_match else None
        
        date_match = re.search(r'([A-Z][a-z]+ \d{1,2}, \d{4})', content)
        issue_date = date_match.group(1) if date_match else None
        
        # Extract document subject from the RBI header
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        header_text = "\n".join(lines[:15])
        
        # Normalize PDF line-break artifacts
        header_text = re.sub(r'([A-Za-z]+)\n([a-z]+)', r'\1\2', header_text)
        
        version_date = None
        version_match = re.search(r'\((?:Updated as on|As on)\s+([A-Z][a-z]+ \d{1,2}, \d{4})\)', header_text, re.IGNORECASE)
        if version_match:
            version_date = version_match.group(1)
            
        validity_status = 'versioned' if version_date else 'unknown'
        
        first_part_upper = content[:2000].upper()
        if "SUPREME COURT OF INDIA" in first_part_upper or "IN THE SUPREME COURT" in first_part_upper:
            document_origin = "NON_RBI"
        elif "RESERVE BANK OF INDIA" in first_part_upper:
            document_origin = "RBI"
        else:
            document_origin = "UNKNOWN"
            
        subject = None
        date_match_header = re.search(
            r'([A-Z][a-z]+ \d{1,2}, \d{4})',
            header_text
        )
        
        if date_match_header:
            after_date = header_text[date_match_header.end():].strip()
            title_parts = []
            stop_markers = ["(Updated", "(As on", "Table of Contents"]
        
            for line in after_date.split('\n'):
                line = line.strip()
        
                if not line:
                    continue
        
                if re.match(r'^\d{1,2}\.', line):
                    break
        
                found_marker = False
        
                for marker in stop_markers:
                    if marker in line:
                        before_marker = line.split(marker, 1)[0].strip()
                        if before_marker:
                            title_parts.append(before_marker)
                        found_marker = True
                        break
        
                if found_marker:
                    break
        
                title_parts.append(line)
        
            if title_parts:
                subject = " ".join(title_parts).strip()
        
        if subject:
            subject = re.sub(r'\[PAGE\s*\d+\]', '', subject, flags=re.IGNORECASE)
            subject = re.sub(r'\s+', ' ', subject).strip()
            
        paras = content.split('\n\n')
        
        for i, p in enumerate(paras):
            p = re.sub(r'\s+', ' ', p).strip()
            if len(p) < 30: continue
            
            doc_type = 'Unknown'
            if subject:
                subj_upper = subject.upper()
                if 'CIRCULAR' in subj_upper:
                    doc_type = 'Circular'
                elif 'DIRECTION' in subj_upper:
                    doc_type = 'Master Direction'
                elif 'NOTIFICATION' in subj_upper:
                    doc_type = 'Notification'
                    
            chunk = {
                'chunk_id': f"RBI-{os.path.basename(filepath)}-{i}",
                'document_id': os.path.basename(filepath),
                'regulator': 'RBI',
                'document_origin': document_origin,
                'document_type': doc_type,
                'circular_number': circular_number,
                'issue_date': issue_date,
                'subject': subject,
                'validity_status': validity_status,
                'version_date': version_date,
                'version_lineage': [],
                'superseded_by_id': None,
                'supersession_edges': [],
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
    output_file = r"D:\REGINTEL-20260820T084445Z-1-001\REGINTEL\regintel\data\processed\rbi_chunks.parquet"
    process_rbi_texts(input_dir, output_file)
