from typing import List, Dict, Any
from backend.app.schemas.eligibility import SchemeEligibilityStatus

def evaluate_scheme_eligibility(scheme_code: str, scheme_name: str, preprocessed_data: Dict[str, Any]) -> SchemeEligibilityStatus:
    profile = preprocessed_data["profile"]
    financials = preprocessed_data["financials"]
    specifics = preprocessed_data["specifics"]
    
    loan_type = financials["loan_type"]
    product_cost = financials["product_cost"]
    amount_required = financials["amount_required"]
    
    reasons: List[str] = []
    status = "ELIGIBLE"
    
    # Global check: Caste must be SC
    if profile["caste"] != "SC":
        return SchemeEligibilityStatus(
            scheme_code=scheme_code,
            scheme_name=scheme_name,
            status="NOT_ELIGIBLE",
            reasons=["Applicant does not meet the beneficiary category requirements."]
        )
        
    if scheme_code == "MFS":
        # 1. Micro Finance Scheme
        if loan_type != "Business":
            return SchemeEligibilityStatus(
                scheme_code=scheme_code,
                scheme_name=scheme_name,
                status="NOT_ELIGIBLE",
                reasons=["Micro Finance Scheme is designed strictly for micro-business projects, not education."]
            )
        
        if product_cost > 140000:
            status = "NOT_ELIGIBLE"
            reasons.append(f"Unit project cost (₹{product_cost:,.2f}) exceeds the maximum permitted limit of ₹1.40 Lakh (₹1,40,000).")
        else:
            reasons.append(f"Unit project cost (₹{product_cost:,.2f}) is within the permitted ₹1.40 Lakh limit.")
            
        max_loan_allowed = min(0.90 * product_cost, 125000)
        if amount_required > max_loan_allowed:
            status = "NOT_ELIGIBLE"
            reasons.append(f"Requested loan amount (₹{amount_required:,.2f}) exceeds maximum allowable loan financing (₹{max_loan_allowed:,.2f} / up to 90% or max ₹1.25 Lakh).")
        else:
            reasons.append(f"Requested loan amount (₹{amount_required:,.2f}) is within the permissible limit of ₹{max_loan_allowed:,.2f}.")
            
        if status == "ELIGIBLE":
            reasons.append("Beneficiary interest rate is set at a concessional 6.5% per annum.")

    elif scheme_code == "TERM_LOAN":
        # 2. Term Loan
        if loan_type != "Business":
            return SchemeEligibilityStatus(
                scheme_code=scheme_code,
                scheme_name=scheme_name,
                status="NOT_ELIGIBLE",
                reasons=["Term Loan is designed strictly for business/industrial projects, not education."]
            )
            
        if product_cost <= 140000:
            status = "NOT_ELIGIBLE"
            reasons.append(f"Unit project cost (₹{product_cost:,.2f}) is too low for Term Loan (requires unit cost > ₹1.40 Lakh up to ₹50.00 Lakh). Consider Micro Finance Scheme.")
        elif product_cost > 5000000:
            status = "NOT_ELIGIBLE"
            reasons.append(f"Unit project cost (₹{product_cost:,.2f}) exceeds the maximum Term Loan limit of ₹50.00 Lakh.")
        else:
            reasons.append(f"Unit project cost (₹{product_cost:,.2f}) falls within the permitted ₹1.40 Lakh – ₹50.00 Lakh bracket.")
            
        max_loan_allowed = min(0.90 * product_cost, 4500000)
        if amount_required > max_loan_allowed:
            status = "NOT_ELIGIBLE"
            reasons.append(f"Requested loan amount (₹{amount_required:,.2f}) exceeds maximum allowable loan limit of ₹{max_loan_allowed:,.2f} (up to 90% or max ₹45.00 Lakh).")
        else:
            reasons.append(f"Requested loan amount (₹{amount_required:,.2f}) is within permissible limit of ₹{max_loan_allowed:,.2f}.")
            
        if status == "ELIGIBLE":
            reasons.append("Beneficiary interest rate is set at 8.0% per annum with extended 7-year repayment.")

    elif scheme_code == "AMFY":
        # 3. Aajeevika Micro-Finance Yojana
        if loan_type != "Business":
            return SchemeEligibilityStatus(
                scheme_code=scheme_code,
                scheme_name=scheme_name,
                status="NOT_ELIGIBLE",
                reasons=["Aajeevika Micro-Finance Yojana is designed strictly for micro-livelihood business activities."]
            )
            
        if product_cost > 140000:
            status = "NOT_ELIGIBLE"
            reasons.append(f"Project cost (₹{product_cost:,.2f}) exceeds the Aajeevika limit of ₹1.40 Lakh.")
        else:
            reasons.append(f"Project cost (₹{product_cost:,.2f}) is within the permitted ₹1.40 Lakh limit.")
            
        max_loan_allowed = min(0.90 * product_cost, 125000)
        if amount_required > max_loan_allowed:
            status = "NOT_ELIGIBLE"
            reasons.append(f"Requested loan amount (₹{amount_required:,.2f}) exceeds max allowable limit of ₹{max_loan_allowed:,.2f}.")
        else:
            reasons.append(f"Requested loan amount (₹{amount_required:,.2f}) is within allowable limit.")
            
        if status == "ELIGIBLE":
            reasons.append("Channelised via NBFC-MFIs at 15% interest rate for quick micro-credit access.")

    elif scheme_code == "UNY":
        # 4. Udyam Nidhi Yojana
        if loan_type != "Business":
            return SchemeEligibilityStatus(
                scheme_code=scheme_code,
                scheme_name=scheme_name,
                status="NOT_ELIGIBLE",
                reasons=["Udyam Nidhi Yojana is designed strictly for small enterprises and business units."]
            )
            
        if product_cost > 500000:
            status = "NOT_ELIGIBLE"
            reasons.append(f"Project cost (₹{product_cost:,.2f}) exceeds the Udyam Nidhi limit of ₹5.00 Lakh.")
        else:
            reasons.append(f"Project cost (₹{product_cost:,.2f}) is within the permitted ₹5.00 Lakh limit.")
            
        max_loan_allowed = min(0.90 * product_cost, 450000)
        if amount_required > max_loan_allowed:
            status = "NOT_ELIGIBLE"
            reasons.append(f"Requested loan amount (₹{amount_required:,.2f}) exceeds maximum allowable loan (₹{max_loan_allowed:,.2f} / max ₹4.50 Lakh).")
        else:
            reasons.append(f"Requested loan amount (₹{amount_required:,.2f}) is within allowable limit of ₹{max_loan_allowed:,.2f}.")
            
        if status == "ELIGIBLE":
            reasons.append("Available via Cooperative Banks (13%) or Small Finance Banks (15%).")

    elif scheme_code == "ELS":
        # 5. Educational Loan Scheme
        if loan_type != "Education":
            return SchemeEligibilityStatus(
                scheme_code=scheme_code,
                scheme_name=scheme_name,
                status="NOT_ELIGIBLE",
                reasons=["Educational Loan Scheme is designed exclusively for higher professional/technical education courses."]
            )
            
        course_name = specifics.get("course_name", "")
        if not course_name:
            return SchemeEligibilityStatus(
                scheme_code=scheme_code,
                scheme_name=scheme_name,
                status="REQUIRES_INFORMATION",
                reasons=["Course details missing. Please provide professional/technical course name."]
            )
            
        max_loan_allowed = min(0.90 * product_cost, 4000000)
        if amount_required > max_loan_allowed:
            status = "NOT_ELIGIBLE"
            reasons.append(f"Requested loan amount (₹{amount_required:,.2f}) exceeds maximum educational loan limit of ₹{max_loan_allowed:,.2f} (up to 90% or max ₹40.00 Lakh).")
        else:
            reasons.append(f"Requested loan amount (₹{amount_required:,.2f}) is within allowable limit of ₹{max_loan_allowed:,.2f}.")
            reasons.append(f"Course '{course_name}' qualifies for 6.5% interest rate and flexible 10-12 year repayment.")

    else:
        status = "REQUIRES_INFORMATION"
        reasons.append("Unrecognized scheme code.")

    return SchemeEligibilityStatus(
        scheme_code=scheme_code,
        scheme_name=scheme_name,
        status=status,
        reasons=reasons
    )

def run_eligibility_engine(all_schemes: List[Any], preprocessed_data: Dict[str, Any]) -> List[SchemeEligibilityStatus]:
    results = []
    for s in all_schemes:
        status_item = evaluate_scheme_eligibility(s.code, s.name, preprocessed_data)
        results.append(status_item)
    return results
