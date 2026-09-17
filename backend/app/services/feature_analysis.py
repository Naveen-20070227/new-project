from typing import Dict, Any

def calculate_scheme_features(scheme: Any, preprocessed_data: Dict[str, Any]) -> Dict[str, float]:
    financials = preprocessed_data["financials"]
    specifics = preprocessed_data["specifics"]
    
    amount_req = financials["amount_required"]
    product_cost = financials["product_cost"]
    loan_type = financials["loan_type"]
    
    # 1. Purpose Match (0.0 to 1.0)
    if scheme.category == loan_type:
        purpose_match = 1.0
    else:
        purpose_match = 0.0
        
    # 2. Loan Amount Match (0.0 to 1.0)
    # Higher score if the scheme can comfortably cover the full requested amount without capping
    max_loan = min(0.90 * product_cost, scheme.max_loan_amount if scheme.max_loan_amount > 0 else 0.90 * product_cost)
    if amount_req <= max_loan:
        # Scale based on how close amount_req is to max_loan (prefer non-crammed room)
        amount_match = 0.85 + 0.15 * (1.0 - (amount_req / max_loan) * 0.3)
    else:
        amount_match = max(0.0, 1.0 - (amount_req - max_loan) / amount_req)
        
    # 3. Project / Course Cost Match (0.0 to 1.0)
    if scheme.max_unit_cost > 0:
        if product_cost <= scheme.max_unit_cost and product_cost >= scheme.min_unit_cost:
            cost_match = 1.0
        else:
            cost_match = 0.5
    else:
        cost_match = 0.9
        
    # 4. Interest Rate Benefit (0.0 to 1.0)
    # Lower interest rate gives higher benefit score. (Base range 6.5% to 15.0%)
    rate = scheme.beneficiary_interest_rate
    interest_benefit = round(max(0.2, min(1.0, 1.0 - (rate - 6.5) / 10.0)), 2)
    
    # 5. Repayment Suitability (0.0 to 1.0)
    # Longer repayment gives lower periodic burden (higher suitability score)
    years = scheme.max_repayment_years
    repayment_suitability = round(min(1.0, years / 10.0), 2)
    
    # 6. Moratorium Benefit (0.0 to 1.0)
    months = scheme.moratorium_months
    moratorium_benefit = round(min(1.0, months / 12.0), 2)
    
    return {
        "purpose_match": round(purpose_match, 2),
        "loan_amount_match": round(amount_match, 2),
        "cost_match": round(cost_match, 2),
        "interest_rate_benefit": round(interest_benefit, 2),
        "repayment_suitability": round(repayment_suitability, 2),
        "moratorium_benefit": round(moratorium_benefit, 2)
    }
