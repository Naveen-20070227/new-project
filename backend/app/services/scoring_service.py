from typing import Dict

# Configurable Scoring Weights (Must total 1.0)
WEIGHTS = {
    "purpose_match": 0.30,
    "loan_amount_match": 0.25,
    "cost_match": 0.15,
    "interest_rate_benefit": 0.15,
    "repayment_suitability": 0.10,
    "moratorium_benefit": 0.05
}

def compute_suitability_score(features: Dict[str, float]) -> float:
    raw_score = 0.0
    for key, weight in WEIGHTS.items():
        feature_val = features.get(key, 0.0)
        raw_score += feature_val * weight
        
    final_score = round(raw_score * 100, 1)
    return max(0.0, min(100.0, final_score))
