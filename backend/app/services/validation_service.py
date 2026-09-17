from typing import List
from backend.app.schemas.eligibility import CheckEligibilityRequest, ValidationResult

def validate_applicant_data(req: CheckEligibilityRequest) -> ValidationResult:
    errors: List[str] = []
    
    # 1. Profile fields
    if not req.profile.name or len(req.profile.name.strip()) < 2:
        errors.append("Applicant name must be at least 2 characters long.")
    if req.profile.age < 18 or req.profile.age > 75:
        errors.append("Applicant age must be between 18 and 75 years.")
    if not req.profile.district or len(req.profile.district.strip()) < 2:
        errors.append("District is required.")
    if not req.profile.state or len(req.profile.state.strip()) < 2:
        errors.append("State is required.")
    if req.profile.caste.strip().upper() != "SC":
        errors.append("This platform is specifically designed for SC (Scheduled Caste) beneficiaries.")
        
    # 2. Financial Requirements
    if req.annual_income <= 0:
        errors.append("Annual income must be a positive numerical value greater than 0.")
    if req.amount_required <= 0:
        errors.append("Required loan amount must be greater than 0.")
    if req.product_cost <= 0:
        errors.append("Product / Course cost must be greater than 0.")
    if req.amount_required > req.product_cost:
        errors.append("Required loan amount cannot exceed the total project or course cost.")
        
    # 3. Loan Type validation
    loan_type = req.loan_type.strip().title()
    if loan_type not in ["Business Loan", "Business", "Education Loan", "Education"]:
        errors.append("Loan type must be either 'Business Loan' or 'Education'.")
        
    if "Business" in loan_type:
        if not req.business_form:
            errors.append("Business loan details (Purpose and Unit) are required when Business Loan is selected.")
        else:
            if not req.business_form.purpose or len(req.business_form.purpose.strip()) < 2:
                errors.append("Business purpose is required.")
            if req.business_form.unit.strip().title() not in ["New", "Expanding"]:
                errors.append("Business unit status must be either 'New' or 'Expanding'.")
    elif "Education" in loan_type:
        if not req.education_form:
            errors.append("Education details (Course Name, College Name, Years) are required when Education is selected.")
        else:
            if not req.education_form.course_name or len(req.education_form.course_name.strip()) < 2:
                errors.append("Course name is required.")
            if not req.education_form.college_name or len(req.education_form.college_name.strip()) < 2:
                errors.append("College/Institution name is required.")
            if req.education_form.number_of_years < 1 or req.education_form.number_of_years > 8:
                errors.append("Duration of course must be between 1 and 8 years.")
                
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors
    )
