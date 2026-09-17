import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from backend.app.models.scheme import Scheme
from backend.app.models.eligibility import EligibilityCheck
from backend.app.models.recommendation import Recommendation
from backend.app.schemas.eligibility import CheckEligibilityRequest
from backend.app.services.validation_service import validate_applicant_data
from backend.app.services.preprocessing_service import preprocess_applicant_data
from backend.app.services.eligibility_engine import run_eligibility_engine
from backend.app.services.feature_analysis import calculate_scheme_features
from backend.app.services.scoring_service import compute_suitability_score
from backend.app.ai.llm_service import llm_service
from backend.app.schemas.recommendation import RecommendationResponse, RecommendedSchemeItem, FinalRecommendation

OFFICIAL_DISCLAIMER = (
    "This recommendation is generated based on the applicant information and official scheme details "
    "provided to the system. The recommendation does not guarantee loan approval. Final eligibility, "
    "verification, and loan approval are subject to the relevant official authority and State Channelising Agency (SCA) "
    "or lending institution."
)

def process_eligibility_and_recommendation(
    db: Session,
    user_id: int,
    request: CheckEligibilityRequest
) -> RecommendationResponse:
    
    # 1. Validation Module
    val_res = validate_applicant_data(request)
    if not val_res.is_valid:
        raise ValueError("; ".join(val_res.errors))
        
    # 2. Preprocessing Module
    prep_data = preprocess_applicant_data(request)
    
    # 3. Retrieve all official schemes from database
    all_schemes = db.query(Scheme).all()
    
    # 4. Deterministic Rule-Based Eligibility Engine
    eligibility_results = run_eligibility_engine(all_schemes, prep_data)
    
    # Organize eligibility results by status
    eligible_list = [r for r in eligibility_results if r.status == "ELIGIBLE"]
    ineligible_list = [r for r in eligibility_results if r.status == "NOT_ELIGIBLE"]
    requires_info_list = [r for r in eligibility_results if r.status == "REQUIRES_INFORMATION"]
    
    # Map scheme metadata for lookup
    scheme_dict = {s.code: s for s in all_schemes}
    
    # 5. Feature Analysis & 6. Suitability Scoring for Eligible Schemes
    candidate_features_list = []
    for r in eligible_list:
        scheme_obj = scheme_dict.get(r.scheme_code)
        if not scheme_obj:
            continue
        feats = calculate_scheme_features(scheme_obj, prep_data)
        score = compute_suitability_score(feats)
        candidate_features_list.append({
            "scheme_code": scheme_obj.code,
            "scheme_name": scheme_obj.name,
            "category": scheme_obj.category,
            "beneficiary_interest_rate": scheme_obj.beneficiary_interest_rate,
            "beneficiary_interest_rate_desc": scheme_obj.beneficiary_interest_rate_desc,
            "max_loan_amount": scheme_obj.max_loan_amount,
            "max_repayment_years": scheme_obj.max_repayment_years,
            "moratorium_months": scheme_obj.moratorium_months,
            "moratorium_desc": scheme_obj.moratorium_desc,
            "repayment_desc": scheme_obj.repayment_desc,
            "features": feats,
            "suitability_score": score
        })
        
    # Sort candidates by suitability score descending
    candidate_features_list.sort(key=lambda x: x["suitability_score"], reverse=True)
    
    # Save Eligibility Check to DB
    fin = prep_data["financials"]
    spec = prep_data["specifics"]
    prof = prep_data["profile"]
    
    check_record = EligibilityCheck(
        user_id=user_id,
        annual_income=fin["annual_income"],
        amount_required=fin["amount_required"],
        product_cost=fin["product_cost"],
        loan_type=fin["loan_type"],
        purpose=spec.get("purpose"),
        unit=spec.get("unit"),
        business_description=spec.get("description"),
        course_name=spec.get("course_name"),
        college_name=spec.get("college_name"),
        number_of_years=spec.get("number_of_years")
    )
    db.add(check_record)
    db.commit()
    db.refresh(check_record)
    
    recommended_items: List[RecommendedSchemeItem] = []
    final_rec: Optional[FinalRecommendation] = None
    ai_available = True
    ai_err_msg = None

    if len(eligible_list) == 0:
        # Zero eligible schemes -> Do NOT call LLM, return actual eligibility status
        ai_available = False
        ai_err_msg = None
        final_rec = FinalRecommendation(
            scheme_id="NONE",
            scheme_name="No Eligible Scheme",
            reason="You are not eligible for any of the available schemes based on the information provided."
        )
    else:
        # Prepare payload for Local Hugging Face LLM Service
        eligible_summary = [{"code": r.scheme_code, "name": r.scheme_name, "reasons": r.reasons} for r in eligible_list]
        ineligible_summary = [{"code": r.scheme_code, "name": r.scheme_name, "reasons": r.reasons} for r in ineligible_list]
        requires_info_summary = [{"code": r.scheme_code, "name": r.scheme_name, "reasons": r.reasons} for r in requires_info_list]
        
        ai_output, ai_error = llm_service.generate_recommendation(
            db=db,
            preprocessed_data=prep_data,
            eligible_schemes_summary=eligible_summary,
            ineligible_schemes_summary=ineligible_summary,
            requires_info_summary=requires_info_summary,
            candidate_features_list=candidate_features_list
        )
        
        if ai_output and not ai_error:
            # Validated AI Output returned
            for item in ai_output.recommendations:
                scheme_obj = scheme_dict.get(item.scheme_id)
                max_loan_desc = f"Up to 90% (Max ₹{scheme_obj.max_loan_amount:,.2f})" if scheme_obj and scheme_obj.max_loan_amount > 0 else "Up to 90% of cost"
                interest_desc = scheme_obj.beneficiary_interest_rate_desc if scheme_obj else "Concessional SC Rate"
                repay_desc = scheme_obj.repayment_desc if scheme_obj else "Standard Repayment"
                mora_desc = scheme_obj.moratorium_desc if scheme_obj else "Standard Moratorium"
                
                recommended_items.append(RecommendedSchemeItem(
                    rank=item.rank,
                    scheme_id=item.scheme_id,
                    scheme_name=item.scheme_name,
                    suitability_score=item.suitability_score,
                    why_recommended=item.why_recommended,
                    important_conditions=item.important_conditions,
                    max_loan_desc=max_loan_desc,
                    interest_rate_desc=interest_desc,
                    repayment_desc=repay_desc,
                    moratorium_desc=mora_desc
                ))
            final_rec = FinalRecommendation(
                scheme_id=ai_output.final_recommendation.scheme_id,
                scheme_name=ai_output.final_recommendation.scheme_name,
                reason=ai_output.final_recommendation.reason
            )
        else:
            # NO FALLBACK RECOMMENDATION: Do not hardcode or fake recommendations
            ai_available = False
            ai_err_msg = ai_error or "AI recommendation is temporarily unavailable. Please try again later."
            recommended_items = []
            final_rec = None
            
    # Construct complete RecommendationResponse
    resp = RecommendationResponse(
        check_id=check_record.id,
        applicant_summary={
            "name": prof["name"],
            "age": prof["age"],
            "caste": prof["caste"],
            "area": prof["area"],
            "district": prof["district"],
            "state": prof["state"],
            "annual_income": fin["annual_income"],
            "amount_required": fin["amount_required"],
            "product_cost": fin["product_cost"],
            "loan_type": fin["loan_type"],
            "specifics": spec
        },
        eligibility_status={
            "eligible": [r.model_dump() for r in eligible_list],
            "ineligible": [r.model_dump() for r in ineligible_list],
            "requires_information": [r.model_dump() for r in requires_info_list]
        },
        suitability_analysis=candidate_features_list,
        recommendations=recommended_items,
        final_recommendation=final_rec,
        ai_available=ai_available,
        ai_error_message=ai_err_msg,
        disclaimer=OFFICIAL_DISCLAIMER
    )
    
    # Save recommendation history in SQLite
    rec_record = Recommendation(
        user_id=user_id,
        check_id=check_record.id,
        rank_1_scheme_code=final_rec.scheme_id if final_rec else None,
        rank_1_suitability_score=recommended_items[0].suitability_score if recommended_items else None,
        full_response_json=json.dumps(resp.model_dump())
    )
    db.add(rec_record)
    db.commit()
    
    return resp
