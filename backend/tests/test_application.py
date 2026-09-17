import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_all_schemes():
    response = client.get("/api/schemes")
    assert response.status_code == 200
    schemes = response.json()
    assert len(schemes) >= 5
    codes = [s["code"] for s in schemes]
    assert "MFS" in codes
    assert "TERM_LOAN" in codes
    assert "AMFY" in codes
    assert "UNY" in codes
    assert "ELS" in codes

def test_otp_flow_and_registration():
    import time
    mobile = f"98{int(time.time() * 1000) % 100000000:08d}"
    otp_resp = client.post("/api/auth/request-otp", json={"mobile_number": mobile})
    assert otp_resp.status_code == 200
    dev_otp = otp_resp.json().get("dev_otp")
    assert dev_otp is not None

    reg_resp = client.post("/api/auth/register", json={
        "beneficiary_name": "Ramesh Kumar",
        "mobile_number": mobile,
        "otp": dev_otp
    })
    assert reg_resp.status_code == 200
    reg_data = reg_resp.json()
    assert "access_token" in reg_data
    
    token = reg_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    prof_resp = client.post("/api/profile", headers=headers, json={
        "name": "Ramesh Kumar",
        "age": 30,
        "gender": "Male",
        "caste": "SC",
        "area": "Rural",
        "district": "Pune",
        "state": "Maharashtra"
    })
    assert prof_resp.status_code == 200

    elig_resp = client.post("/api/eligibility/check", headers=headers, json={
        "profile": {
            "name": "Ramesh Kumar",
            "age": 30,
            "gender": "Male",
            "caste": "SC",
            "area": "Rural",
            "district": "Pune",
            "state": "Maharashtra"
        },
        "annual_income": 150000,
        "amount_required": 100000,
        "product_cost": 120000,
        "loan_type": "Business Loan",
        "business_form": {
            "purpose": "Dairy Farming",
            "unit": "New",
            "description": "Purchase of two milch cows"
        }
    })
    assert elig_resp.status_code == 200
    elig_data = elig_resp.json()
    assert len(elig_data["eligibility_status"]["eligible"]) > 0

def test_zero_eligible_schemes_no_ai_call():
    import time
    mobile = f"97{int(time.time() * 1000) % 100000000:08d}"
    otp_resp = client.post("/api/auth/request-otp", json={"mobile_number": mobile})
    dev_otp = otp_resp.json().get("dev_otp")

    reg_resp = client.post("/api/auth/register", json={
        "beneficiary_name": "Suresh Kumar",
        "mobile_number": mobile,
        "otp": dev_otp
    })
    token = reg_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Submit valid inputs with extremely high product cost (₹90 Lakhs) exceeding all business loan scheme limits
    elig_resp = client.post("/api/eligibility/check", headers=headers, json={
        "profile": {
            "name": "Suresh Kumar",
            "age": 30,
            "gender": "Male",
            "caste": "SC",
            "area": "Urban",
            "district": "Lucknow",
            "state": "Uttar Pradesh"
        },
        "annual_income": 500000,
        "amount_required": 8000000,
        "product_cost": 9000000,
        "loan_type": "Business Loan",
        "business_form": {
            "purpose": "Heavy Industrial Factory",
            "unit": "New",
            "description": "Large scale manufacturing unit"
        }
    })
    assert elig_resp.status_code == 200
    data = elig_resp.json()
    assert len(data["eligibility_status"]["eligible"]) == 0
    assert data["ai_available"] == False
    assert data["final_recommendation"]["scheme_id"] == "NONE"

def test_zero_trust_unauthorized():
    res = client.get("/api/profile")
    assert res.status_code == 401

def test_emi_calculator_api():
    post_res = client.post("/api/emi/calculate", json={"amount": 125000, "rate": 6.5, "tenure_years": 3})
    assert post_res.status_code == 200
    pdata = post_res.json()
    assert pdata["monthly_instalment"] > 0
    assert pdata["quarterly_instalment"] > pdata["monthly_instalment"]
    assert pdata["total_payment"] > pdata["amount"]

    get_res = client.get("/api/emi/calculate?amount=125000&rate=6.5&tenure_years=3")
    assert get_res.status_code == 200
    gdata = get_res.json()
    assert gdata["monthly_instalment"] == pdata["monthly_instalment"]

def test_geo_locator_api():
    all_res = client.get("/api/geo/agencies")
    assert all_res.status_code == 200
    adata = all_res.json()
    assert adata["total"] >= 10

    search_res = client.get("/api/geo/agencies?search=Maharashtra")
    assert search_res.status_code == 200
    sdata = search_res.json()
    assert sdata["total"] > 0
    assert any(a["state"] == "Maharashtra" for a in sdata["agencies"])
