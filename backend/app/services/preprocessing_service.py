from typing import Dict, Any
from backend.app.schemas.eligibility import CheckEligibilityRequest

def preprocess_applicant_data(req: CheckEligibilityRequest) -> Dict[str, Any]:
    raw_type = req.loan_type.strip().title()
    normalized_type = "Business" if "Business" in raw_type else "Education"
    
    normalized_profile = {
        "name": req.profile.name.strip().title(),
        "age": int(req.profile.age),
        "gender": req.profile.gender.strip().title(),
        "caste": "SC",
        "area": req.profile.area.strip().title(),
        "district": req.profile.district.strip().title(),
        "state": req.profile.state.strip().title(),
    }
    
    financials = {
        "annual_income": round(float(req.annual_income), 2),
        "amount_required": round(float(req.amount_required), 2),
        "product_cost": round(float(req.product_cost), 2),
        "loan_type": normalized_type
    }
    
    specifics = {}
    if normalized_type == "Business" and req.business_form:
        specifics = {
            "purpose": req.business_form.purpose.strip().title(),
            "unit": req.business_form.unit.strip().title(),
            "description": req.business_form.description.strip() if req.business_form.description else ""
        }
    elif normalized_type == "Education" and req.education_form:
        specifics = {
            "course_name": req.education_form.course_name.strip().title(),
            "college_name": req.education_form.college_name.strip().title(),
            "number_of_years": int(req.education_form.number_of_years)
        }
        
    return {
        "profile": normalized_profile,
        "financials": financials,
        "specifics": specifics
    }
