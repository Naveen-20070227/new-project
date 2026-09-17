from sqlalchemy.orm import Session
from backend.app.models.scheme import Scheme

INITIAL_SCHEMES = [
    {
        "code": "MFS",
        "name": "Micro Finance Scheme (MFS)",
        "category": "Business",
        "target_cost_desc": "Units costing up to ₹1.40 lakh",
        "min_unit_cost": 0.0,
        "max_unit_cost": 140000.0,
        "max_loan_pct": 90.0,
        "min_loan_amount": 0.0,
        "max_loan_amount": 125000.0,
        "beneficiary_interest_rate": 6.5,
        "beneficiary_interest_rate_desc": "6.5% p.a. for SC beneficiaries",
        "intermediary_rate": "2.5% p.a. for SCA/CA",
        "repayment_desc": "Maximum 3 years in quarterly instalments",
        "max_repayment_years": 3.0,
        "moratorium_desc": "3 months moratorium period",
        "moratorium_months": 3,
        "short_description": "Concessional micro-credit financing for small income-generating units costing up to ₹1.40 Lakh.",
        "full_description": (
            "The Micro Finance Scheme (MFS) provides prompt micro-credit financing to SC beneficiaries for small income-generating activities. "
            "It covers project units costing up to ₹1.40 lakh, offering up to 90% loan assistance (maximum ₹1.25 lakh per unit) at a highly concessional 6.5% annual interest rate."
        )
    },
    {
        "code": "TERM_LOAN",
        "name": "Term Loan Scheme",
        "category": "Business",
        "target_cost_desc": "Units costing > ₹1.40 lakh up to ₹50.00 lakh",
        "min_unit_cost": 140001.0,
        "max_unit_cost": 5000000.0,
        "max_loan_pct": 90.0,
        "min_loan_amount": 125001.0,
        "max_loan_amount": 4500000.0,
        "beneficiary_interest_rate": 8.0,
        "beneficiary_interest_rate_desc": "8.0% p.a. for SC beneficiaries",
        "intermediary_rate": "4.0% p.a. for SCA/CA",
        "repayment_desc": "Maximum 7 years in quarterly instalments",
        "max_repayment_years": 7.0,
        "moratorium_desc": "6 months moratorium (12 months for plantation/construction)",
        "moratorium_months": 6,
        "short_description": "Medium & long-term credit for business enterprises and industrial units costing up to ₹50.00 Lakh.",
        "full_description": (
            "The Term Loan Scheme supports commercial, industrial, agricultural, and service sector projects. "
            "For projects costing between ₹1.40 lakh and ₹50.00 lakh, NSFDC/SCA provides up to 90% financing (above ₹1.25 lakh up to ₹45 lakh per unit) "
            "at an attractive 8.0% annual interest rate with up to 7 years repayment period."
        )
    },
    {
        "code": "AMFY",
        "name": "Aajeevika Micro-Finance Yojana",
        "category": "Business",
        "target_cost_desc": "Projects costing up to ₹1.40 lakh",
        "min_unit_cost": 0.0,
        "max_unit_cost": 140000.0,
        "max_loan_pct": 90.0,
        "min_loan_amount": 0.0,
        "max_loan_amount": 125000.0,
        "beneficiary_interest_rate": 15.0,
        "beneficiary_interest_rate_desc": "15.0% p.a. via NBFC-MFIs",
        "intermediary_rate": "5.0% p.a. for NBFC-MFI",
        "repayment_desc": "Maximum 3 years in quarterly instalments",
        "max_repayment_years": 3.0,
        "moratorium_desc": "3 months moratorium period",
        "moratorium_months": 3,
        "short_description": "Rapid micro-finance credit delivery for micro-livelihood projects via NBFC-MFIs.",
        "full_description": (
            "Aajeevika Micro-Finance Yojana delivers quick micro-loans for livelihood activities up to ₹1.40 lakh through Non-Banking Financial Company - Micro Finance Institutions (NBFC-MFIs). "
            "Provides loan assistance up to ₹1.25 lakh (90% of cost) with a 3-year quarterly repayment schedule."
        )
    },
    {
        "code": "UNY",
        "name": "Udyam Nidhi Yojana (UNY)",
        "category": "Business",
        "target_cost_desc": "Projects/units costing up to ₹5.00 lakh",
        "min_unit_cost": 0.0,
        "max_unit_cost": 500000.0,
        "max_loan_pct": 90.0,
        "min_loan_amount": 0.0,
        "max_loan_amount": 450000.0,
        "beneficiary_interest_rate": 13.0,
        "beneficiary_interest_rate_desc": "13.0% via Cooperative Banks / 15.0% via SFBs",
        "intermediary_rate": "Channelised via Cooperative / Small Finance Banks",
        "repayment_desc": "Maximum 5 years in quarterly/half-yearly instalments",
        "max_repayment_years": 5.0,
        "moratorium_desc": "3 months moratorium period",
        "moratorium_months": 3,
        "short_description": "Financial assistance for small business units costing up to ₹5.00 Lakh via cooperative and SFBs.",
        "full_description": (
            "Udyam Nidhi Yojana assists SC entrepreneurs setting up or expanding small enterprises costing up to ₹5.00 lakh. "
            "Provides loans up to ₹4.50 lakh (90% of project cost) at 13% interest via Cooperative Banks and 15% via Small Finance Banks with a 5-year repayment window."
        )
    },
    {
        "code": "ELS",
        "name": "Educational Loan Scheme (ELS)",
        "category": "Education",
        "target_cost_desc": "Regular full-time professional/technical recognized courses",
        "min_unit_cost": 0.0,
        "max_unit_cost": 0.0, # Unlimited course cost bracket
        "max_loan_pct": 90.0,
        "min_loan_amount": 0.0,
        "max_loan_amount": 4000000.0,
        "beneficiary_interest_rate": 6.5,
        "beneficiary_interest_rate_desc": "6.5% p.a. for SC students",
        "intermediary_rate": "2.5% p.a. for CA",
        "repayment_desc": "Up to 10–12 years repayment tenure",
        "max_repayment_years": 12.0,
        "moratorium_desc": "Course period + 1 year (or up to 6 months post-disbursement)",
        "moratorium_months": 12,
        "short_description": "Concessional educational loan up to ₹40.00 Lakh for professional & technical degree courses.",
        "full_description": (
            "Educational Loan Scheme (ELS) empowers eligible SC students pursuing full-time professional or technical courses in India or abroad. "
            "Finances up to 90% of course fees or max ₹40.00 lakh at a concessional interest rate of 6.5% per annum, with repayment extended up to 10-12 years and course-duration moratorium."
        )
    }
]

def seed_schemes(db: Session):
    for s_data in INITIAL_SCHEMES:
        existing = db.query(Scheme).filter(Scheme.code == s_data["code"]).first()
        if not existing:
            new_scheme = Scheme(**s_data)
            db.add(new_scheme)
    db.commit()
