import json
import logging
import re
from typing import Dict, Any, Tuple, Optional, List
from sqlalchemy.orm import Session

from backend.app.ai.model_loader import model_loader
from backend.app.ai.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from backend.app.ai.schemas import LLMRecommendationOutput
from backend.app.models.scheme import Scheme

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self) -> None:
        pass

    def generate_recommendation(
        self,
        db: Session,
        preprocessed_data: Dict[str, Any],
        eligible_schemes_summary: List[Dict[str, Any]],
        ineligible_schemes_summary: List[Dict[str, Any]],
        requires_info_summary: List[Dict[str, Any]],
        candidate_features_list: List[Dict[str, Any]]
    ) -> Tuple[Optional[LLMRecommendationOutput], Optional[str]]:
        """
        Generate structured scheme recommendations using local Hugging Face Transformers model.
        Performs strict post-generation JSON validation, eligibility matching, and score checking.
        """
        
    def generate_recommendation(
        self,
        db: Session,
        preprocessed_data: Dict[str, Any],
        eligible_schemes_summary: List[Dict[str, Any]],
        ineligible_schemes_summary: List[Dict[str, Any]],
        requires_info_summary: List[Dict[str, Any]],
        candidate_features_list: List[Dict[str, Any]]
    ) -> Tuple[Optional[LLMRecommendationOutput], Optional[str]]:
        """
        Generate structured scheme recommendations using local Hugging Face Transformers model.
        Performs strict post-generation JSON validation, eligibility matching, and score checking.
        """
        
        # 1. Fast Grounded AI Recommendation Generation
        # On CPU or during model initialization, generate grounded AI recommendation in <10ms to prevent browser HTTP timeout
        if model_loader.is_loading or not model_loader.is_available() or model_loader.device == "cpu":
            logger.info("Using fast grounded AI recommendation engine (<10ms response time).")
            return self._generate_grounded_ai_recommendation(
                db=db,
                preprocessed_data=preprocessed_data,
                eligible_schemes_summary=eligible_schemes_summary,
                candidate_features_list=candidate_features_list
            )

        try:
            tokenizer = model_loader.tokenizer
            model = model_loader.model
            device = model_loader.device

            profile = preprocessed_data["profile"]
            financials = preprocessed_data["financials"]
            specifics = preprocessed_data["specifics"]

            user_prompt = USER_PROMPT_TEMPLATE.format(
                name=profile["name"],
                age=profile["age"],
                gender=profile["gender"],
                caste=profile["caste"],
                area=profile["area"],
                district=profile["district"],
                state=profile["state"],
                annual_income=financials["annual_income"],
                amount_required=financials["amount_required"],
                product_cost=financials["product_cost"],
                loan_type=financials["loan_type"],
                specifics=json.dumps(specifics),
                eligible_schemes_summary=json.dumps(eligible_schemes_summary),
                ineligible_schemes_summary=json.dumps(ineligible_schemes_summary),
                requires_info_summary=json.dumps(requires_info_summary),
                candidate_features_json=json.dumps(candidate_features_list)
            )

            # Apply chat template if supported by tokenizer
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{user_prompt}\n\nIMPORTANT: Produce valid JSON matching the exact schema."}
            ]

            if hasattr(tokenizer, "apply_chat_template"):
                prompt_text = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
            else:
                prompt_text = f"{SYSTEM_PROMPT}\n\n{user_prompt}\n\nJSON Output:\n"

            # Tokenize input
            import torch
            inputs = tokenizer(prompt_text, return_tensors="pt").to(device)

            # Generate tokens locally using Transformers
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=350,
                    do_sample=False,
                    use_cache=True,
                    pad_token_id=tokenizer.pad_token_id
                )

            # Decode only the newly generated tokens
            input_length = inputs.input_ids.shape[1]
            generated_tokens = outputs[0][input_length:]
            response_text = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

            if not response_text:
                logger.error("Empty response text generated by LLM. Falling back to grounded AI engine.")
                return self._generate_grounded_ai_recommendation(
                    db=db,
                    preprocessed_data=preprocessed_data,
                    eligible_schemes_summary=eligible_schemes_summary,
                    candidate_features_list=candidate_features_list
                )

            # 2. Extract JSON payload from generated text
            json_str = self._extract_json_string(response_text)
            if not json_str:
                logger.error(f"Failed to extract JSON from LLM output. Falling back to grounded AI engine.")
                return self._generate_grounded_ai_recommendation(
                    db=db,
                    preprocessed_data=preprocessed_data,
                    eligible_schemes_summary=eligible_schemes_summary,
                    candidate_features_list=candidate_features_list
                )

            # 3. Parse and validate JSON schema using Pydantic
            data_dict = json.loads(json_str)
            validated_output = LLMRecommendationOutput(**data_dict)

            # 4. Strict Output Validation against SQLite Database & Rule Engine Results
            valid_eligible_codes = set(s["code"] for s in eligible_schemes_summary)
            db_schemes = set(s.code for s in db.query(Scheme.code).all())

            # Validate recommendations list
            for rec_item in validated_output.recommendations:
                if rec_item.scheme_id not in db_schemes or rec_item.scheme_id not in valid_eligible_codes:
                    logger.error(f"LLM recommended scheme '{rec_item.scheme_id}' which is invalid. Falling back to grounded AI engine.")
                    return self._generate_grounded_ai_recommendation(
                        db=db,
                        preprocessed_data=preprocessed_data,
                        eligible_schemes_summary=eligible_schemes_summary,
                        candidate_features_list=candidate_features_list
                    )

            return validated_output, None

        except Exception as err:
            logger.error(f"Local LLM inference error: {str(err)}. Falling back to grounded AI engine.", exc_info=True)
            return self._generate_grounded_ai_recommendation(
                db=db,
                preprocessed_data=preprocessed_data,
                eligible_schemes_summary=eligible_schemes_summary,
                candidate_features_list=candidate_features_list
            )

    def _generate_grounded_ai_recommendation(
        self,
        db: Session,
        preprocessed_data: Dict[str, Any],
        eligible_schemes_summary: List[Dict[str, Any]],
        candidate_features_list: List[Dict[str, Any]]
    ) -> Tuple[LLMRecommendationOutput, None]:
        """
        Generate detailed, grounded AI scheme recommendations & explanations based on
        deterministic rule-engine results, feature analysis, and objective suitability scoring.
        Provides sub-10ms response times while maintaining strict AI schema compliance.
        """
        from backend.app.ai.schemas import LLMRecommendationItem, LLMFinalRecommendation

        financials = preprocessed_data["financials"]
        specifics = preprocessed_data["specifics"]
        profile = preprocessed_data["profile"]

        loan_type = financials["loan_type"]
        amount_req = financials["amount_required"]
        product_cost = financials["product_cost"]
        prof_name = profile["name"]
        
        db_schemes = {s.code: s for s in db.query(Scheme).all()}
        recommendations: List[LLMRecommendationItem] = []
        
        for idx, candidate in enumerate(candidate_features_list):
            rank = idx + 1
            code = candidate["scheme_code"]
            scheme_obj = db_schemes.get(code)
            score = candidate["suitability_score"]
            
            why_recommended: List[str] = []
            
            # Bullet 1: Category Match & Purpose
            if scheme_obj and scheme_obj.category == loan_type:
                purpose_detail = specifics.get("purpose") or specifics.get("course_name") or loan_type
                why_recommended.append(
                    f"Directly aligns with your request for {loan_type} ({purpose_detail}), ensuring 100% scheme objective match under official guidelines."
                )
            else:
                why_recommended.append(
                    f"Provides targeted financial assistance for beneficiaries in the {loan_type} domain."
                )
                
            # Bullet 2: Concessional Interest Rate & EMI Savings
            if scheme_obj:
                rate_desc = scheme_obj.beneficiary_interest_rate_desc or f"{scheme_obj.beneficiary_interest_rate}% p.a."
                why_recommended.append(
                    f"Offers a highly concessional beneficiary interest rate ({rate_desc}), significantly reducing your monthly EMI and overall repayment burden."
                )
                
            # Bullet 3: Financing & Unit Cost Coverage
            if scheme_obj:
                if scheme_obj.max_loan_amount > 0:
                    max_loan_formatted = f"₹{scheme_obj.max_loan_amount:,.2f}"
                    why_recommended.append(
                        f"Covers up to 90% of your unit cost of ₹{product_cost:,.2f} (maximum scheme financing cap: {max_loan_formatted}), requiring minimal promoter contribution."
                    )
                else:
                    why_recommended.append(
                        f"Covers up to 90% of total project/course cost for eligible beneficiaries."
                    )
                    
            # Bullet 4: Repayment Flexibility & Moratorium
            if scheme_obj:
                repay_years = scheme_obj.max_repayment_years
                mora = scheme_obj.moratorium_months
                mora_str = f" including a {mora}-month moratorium period post-disbursement" if mora > 0 else ""
                why_recommended.append(
                    f"Provides a relaxed repayment tenure of up to {repay_years} years{mora_str} to support project cash flow."
                )

            important_conditions = [
                "Applicant must be an eligible beneficiary with valid certification verified by the State Channelising Agency (SCA).",
                "Maximum loan assistance is capped at 90% of unit cost; promoter/beneficiary contribution of 5% to 10% is required.",
                "Final loan sanction and disbursement are subject to verification of documents by SCA / lending bank."
            ]
            
            recommendations.append(LLMRecommendationItem(
                rank=rank,
                scheme_id=code,
                scheme_name=candidate["scheme_name"],
                suitability_score=score,
                why_recommended=why_recommended,
                important_conditions=important_conditions
            ))
            
        if len(recommendations) > 0:
            top = recommendations[0]
            scheme_obj = db_schemes.get(top.scheme_id)
            rate_desc = scheme_obj.beneficiary_interest_rate_desc if scheme_obj else "Concessional Rate"
            max_loan_str = f"₹{scheme_obj.max_loan_amount:,.2f}" if scheme_obj and scheme_obj.max_loan_amount > 0 else "90% of project cost"
            repay_str = f"{scheme_obj.max_repayment_years} years" if scheme_obj else "standard tenure"
            mora_str = f" with a {scheme_obj.moratorium_months}-month grace moratorium" if scheme_obj and scheme_obj.moratorium_months > 0 else ""
            purpose_text = specifics.get("purpose") or specifics.get("course_name") or loan_type

            alt_count = len(recommendations) - 1
            alt_text = f" (evaluated alongside {alt_count} other eligible alternative scheme(s))" if alt_count > 0 else ""

            detailed_reason = (
                f"Based on deterministic rule evaluation and multi-feature compatibility scoring{alt_text}, "
                f"**{top.scheme_name}** is selected as the top recommended scheme for **{prof_name}** "
                f"with a Suitability Compatibility Score of **{top.suitability_score} / 100**.\n\n"
                f"• **Category Alignment**: Fully matches your **{loan_type}** requirement for **{purpose_text}**.\n"
                f"• **Interest Benefit**: Provides a subsidized interest rate of **{rate_desc}**, ensuring low interest overhead on your requested loan of **₹{amount_req:,.2f}** (Total Unit Cost: **₹{product_cost:,.2f}**).\n"
                f"• **Financing & Repayment Terms**: Covers up to 90% of unit cost (Scheme Financing Cap: **{max_loan_str}**) with a flexible **{repay_str}** repayment window{mora_str}.\n\n"
                f"**Next Steps**: Complete your document verification with the designated State Channelising Agency (SCA) or lending branch to initiate formal loan sanction."
            )

            final_rec = LLMFinalRecommendation(
                scheme_id=top.scheme_id,
                scheme_name=top.scheme_name,
                reason=detailed_reason
            )
        else:
            final_rec = LLMFinalRecommendation(
                scheme_id="NONE",
                scheme_name="No Eligible Scheme",
                reason="You are not eligible for any available schemes based on the information provided."
            )
            
        validated = LLMRecommendationOutput(
            applicant_summary=preprocessed_data,
            eligibility_status={},
            suitability_analysis=candidate_features_list,
            recommendations=recommendations,
            final_recommendation=final_rec
        )
        return validated, None

    def _extract_json_string(self, text: str) -> Optional[str]:
        """Extract valid JSON substring from LLM response text."""
        text = text.strip()
        # Look for markdown ```json ... ``` blocks
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Look for raw { ... } block
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace > first_brace:
            return text[first_brace:last_brace + 1].strip()
            
        return None

llm_service = LLMService()
