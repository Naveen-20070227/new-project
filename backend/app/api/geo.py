from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, ConfigDict

router = APIRouter(prefix="/geo", tags=["Geo Locator Directory"])

SCA_DIRECTORY = [
    {
        "state": "Maharashtra",
        "name": "Mahatma Phule Backward Class Development Corporation Ltd.",
        "address": "Administrative Building, 4th Floor, Ramkrishna Chemburkar Marg, Chembur, Mumbai - 400071",
        "phone": "022-25220803 / 25220804",
        "website": "https://mpbcdc.maharashtra.gov.in"
    },
    {
        "state": "Uttar Pradesh",
        "name": "U.P. Scheduled Castes Finance & Development Corporation Ltd.",
        "address": "TC-46/V-Vibhuti Khand, Gomti Nagar, Lucknow - 226010",
        "phone": "0522-2307684 / 2307683",
        "website": "http://upscfdc.up.gov.in"
    },
    {
        "state": "Tamil Nadu",
        "name": "Tamil Nadu Adi Dravidar Housing & Development Corporation (TAHDCO)",
        "address": "No. 31, Cenotaph Road, 2nd Lane, Teynampet, Chennai - 600018",
        "phone": "044-24310214 / 24310215",
        "website": "https://tahdco.tn.gov.in"
    },
    {
        "state": "Karnataka",
        "name": "Dr. B.R. Ambedkar Development Corporation Ltd.",
        "address": "9th Floor, Vishveshwaraiah Main Tower, Dr. B.R. Ambedkar Veedhi, Bengaluru - 560001",
        "phone": "080-22864811 / 22864812",
        "website": "https://adcl.karnataka.gov.in"
    },
    {
        "state": "Punjab",
        "name": "Punjab Scheduled Castes Land Development & Finance Corporation",
        "address": "SCO 101-103, Sector 17-C, Chandigarh - 160017",
        "phone": "0172-2704381 / 2704383",
        "website": "http://pscldfc.punjab.gov.in"
    },
    {
        "state": "Telangana",
        "name": "Telangana Scheduled Castes Cooperative Development Corporation Ltd.",
        "address": "DSS Bhavan, Masab Tank, Hyderabad - 500028",
        "phone": "040-23391624 / 23391625",
        "website": "https://tscorporation.telangana.gov.in"
    },
    {
        "state": "Andhra Pradesh",
        "name": "A.P. Scheduled Castes Co-op Finance Corporation Ltd.",
        "address": "VC & MD Office, Tadepalli, Guntur District, Vijayawada - 520001",
        "phone": "0866-2498222",
        "website": "https://apscfc.ap.gov.in"
    },
    {
        "state": "Delhi",
        "name": "Delhi SC/ST/OBC/Minorities Development & Finance Corporation (DSFDC)",
        "address": "2-3, Ambedkar Bhawan, Institutional Area, Sector-16, Rohini, New Delhi - 110089",
        "phone": "011-27572701 / 27572702",
        "website": "http://dsfdc.delhi.gov.in"
    },
    {
        "state": "West Bengal",
        "name": "West Bengal Scheduled Castes, Scheduled Tribes & OBC Development & Finance Corporation",
        "address": "CF-217/A1, Sector-I, Salt Lake City, Kolkata - 700064",
        "phone": "033-23348121 / 23348122",
        "website": "http://wbscstdfc.gov.in"
    },
    {
        "state": "Bihar",
        "name": "Bihar State Scheduled Castes Co-operative Development Corporation Ltd.",
        "address": "Maurya Lok Complex, Block A, 2nd Floor, Patna - 800001",
        "phone": "0612-2215432",
        "website": "http://scwelfare.bih.nic.in"
    },
    {
        "state": "Gujarat",
        "name": "Gujarat Scheduled Castes Development Corporation",
        "address": "Block No. 14, 4th Floor, Dr. Jivraj Mehta Bhavan, Gandhinagar - 382010",
        "phone": "079-23253724 / 23253725",
        "website": "https://sje.gujarat.gov.in"
    },
    {
        "state": "Madhya Pradesh",
        "name": "M.P. State Scheduled Castes Finance & Development Corporation",
        "address": "Rajiv Gandhi Bhawan, 35, Shyamla Hills, Bhopal - 462002",
        "phone": "0755-2661582 / 2661583",
        "website": "http://scwelfare.mp.gov.in"
    }
]

class AgencyItem(BaseModel):
    state: str
    name: str
    address: str
    phone: str
    website: str

    model_config = ConfigDict(from_attributes=True)

class GeoAgencyResponse(BaseModel):
    total: int
    agencies: List[AgencyItem]

    model_config = ConfigDict(from_attributes=True)

@router.get("/agencies", response_model=GeoAgencyResponse)
def get_channelising_agencies(search: Optional[str] = Query(None, description="Search by state or agency name")):
    """Retrieve State Channelising Agencies (SCAs) directory, optionally filtered by state or agency name."""
    if not search or not search.strip():
        return GeoAgencyResponse(total=len(SCA_DIRECTORY), agencies=SCA_DIRECTORY)

    q = search.strip().lower()
    filtered = [
        item for item in SCA_DIRECTORY
        if q in item["state"].lower() or q in item["name"].lower() or q in item["address"].lower()
    ]
    return GeoAgencyResponse(total=len(filtered), agencies=filtered)
