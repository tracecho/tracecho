import json
from typing import Dict, List, Any

# A deterministic answer evaluator that leverages Verification Agent patterns and simple heuristics.
# In a full research setup this could also use LLM-as-a-judge for 'relevance' and 'faithfulness'.

def evaluate_citations(citations: List[Dict[str, Any]], expected_chunk_ids: List[str]) -> bool:
    """Check if citations correctly map to expected evidence chunks."""
    if not citations or not expected_chunk_ids:
        return False
    # Check if any cited chunk is in expected chunks (loose citation)
    return any(cit.get("chunk_id") in expected_chunk_ids for cit in citations)

def calculate_citation_accuracy(answers: List[Dict[str, Any]], benchmark: List[Dict]) -> float:
    """Percentage of answers with valid citations when expected."""
    correct = 0
    total = 0
    for idx, ans in enumerate(answers):
        bitem = benchmark[idx]
        if not bitem.get("answerable"):
            continue
        total += 1
        expected = bitem.get("expected_chunk_ids", [])
        if evaluate_citations(ans.get("citations", []), expected):
            correct += 1
            
    return correct / total if total > 0 else 0.0

def calculate_hallucination_rate(answers: List[Dict[str, Any]], benchmark: List[Dict]) -> float:
    """Calculate the rate of hallucinated answers (answering when unanswerable)."""
    hallucinations = 0
    total = 0
    for idx, ans in enumerate(answers):
        bitem = benchmark[idx]
        if bitem.get("answerable"):
            continue # We only measure hallucination on unanswerable questions here
            
        total += 1
        insufficient_flag = ans.get("evidence_insufficient", False)
        # If the system tried to answer an unanswerable question instead of flagging insufficient
        if not insufficient_flag:
            hallucinations += 1
            
    return hallucinations / total if total > 0 else 0.0

def evaluate_verification_agent(answers: List[Dict], benchmark: List[Dict]) -> dict:
    """Evaluate Verification Agent precision/recall on detecting insufficient evidence."""
    tp, fp, tn, fn = 0, 0, 0, 0
    
    for idx, ans in enumerate(answers):
        bitem = benchmark[idx]
        # For this metric we look at the 'verification_output' inside the answers structure
        verif = ans.get("_verification_output", {})
        if not verif:
            continue
            
        predicted_insufficient = (verif.get("recommended_action") == "INSUFFICIENT_EVIDENCE")
        actual_insufficient = not bitem.get("answerable")
        
        if actual_insufficient and predicted_insufficient:
            tp += 1
        elif actual_insufficient and not predicted_insufficient:
            fn += 1
        elif not actual_insufficient and predicted_insufficient:
            fp += 1
        else:
            tn += 1
            
    return {
        "True Positives": tp,
        "False Positives": fp,
        "True Negatives": tn,
        "False Negatives": fn,
    }
