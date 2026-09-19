from typing import List, Optional
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
import httpx
import math

router = APIRouter(prefix="/geo", tags=["Geo Locator Directory"])

# Complete 79 State Channelising Agencies (SCAs), Regional Rural Banks & Partner Bank Locations across India
PIN_DATASET = [
  {
    "id": "bank_1",
    "name": "Bihar Gramin Bank",
    "lat": 25.6093239,
    "lng": 85.1235252,
    "description": "Regional Rural Bank - Patna, Bihar"
  },
  {
    "id": "bank_2",
    "name": "Maharashtra Gramin Bank",
    "lat": 19.877263,
    "lng": 75.3390241,
    "description": "Regional Rural Bank - Aurangabad, Maharashtra"
  },
  {
    "id": "bank_3",
    "name": "Jharkhand Gramin Bank",
    "lat": 23.3700501,
    "lng": 85.3250387,
    "description": "Regional Rural Bank - Ranchi, Jharkhand"
  },
  {
    "id": "bank_4",
    "name": "Haryana Gramin Bank",
    "lat": 28.9010899,
    "lng": 76.5801935,
    "description": "Regional Rural Bank - Rohtak, Haryana"
  },
  {
    "id": "bank_5",
    "name": "Gujarat Gramin Bank",
    "lat": 21.7080427,
    "lng": 72.9956936,
    "description": "Regional Rural Bank - Bharuch, Gujarat"
  },
  {
    "id": "bank_6",
    "name": "Telangana Grameena Bank",
    "lat": 17.360589,
    "lng": 78.4740613,
    "description": "Regional Rural Bank - Hyderabad, Telangana"
  },
  {
    "id": "bank_7",
    "name": "Rajasthan Gramin Bank",
    "lat": 26.2967719,
    "lng": 73.0351433,
    "description": "Regional Rural Bank - Jodhpur, Rajasthan"
  },
  {
    "id": "bank_8",
    "name": "Uttar Pradesh Gramin Bank",
    "lat": 26.8381,
    "lng": 80.9346001,
    "description": "Regional Rural Bank - Lucknow, Uttar Pradesh"
  },
  {
    "id": "bank_9",
    "name": "Kerala Grameena Bank",
    "lat": 11.1065685,
    "lng": 76.1101742,
    "description": "Regional Rural Bank - Malappuram, Kerala"
  },
  {
    "id": "bank_10",
    "name": "Uttarakhand Gramin Bank",
    "lat": 30.3255646,
    "lng": 78.0436813,
    "description": "Regional Rural Bank - Dehradun, Uttarakhand"
  },
  {
    "id": "bank_11",
    "name": "Tripura Gramin Bank",
    "lat": 23.8312377,
    "lng": 91.2823821,
    "description": "Regional Rural Bank - Agartala, Tripura"
  },
  {
    "id": "bank_13",
    "name": "Assam Gramin Bank",
    "lat": 26.1805978,
    "lng": 91.753943,
    "description": "Regional Rural Bank - Guwahati, Assam"
  },
  {
    "id": "bank_14",
    "name": "Andhra Pradesh Grameena Bank",
    "lat": 16.2915189,
    "lng": 80.4541588,
    "description": "Regional Rural Bank - Guntur, Andhra Pradesh"
  },
  {
    "id": "bank_15",
    "name": "Punjab Gramin Bank",
    "lat": 31.3856476,
    "lng": 75.3053304,
    "description": "Regional Rural Bank - Kapurthala, Punjab"
  },
  {
    "id": "bank_16",
    "name": "Tamil Nadu Grama Bank",
    "lat": 11.6469616,
    "lng": 78.2106958,
    "description": "Regional Rural Bank - Salem, Tamil Nadu"
  },
  {
    "id": "bank_17",
    "name": "Madhaya Pradesh Gramin Bank",
    "lat": 22.7203616,
    "lng": 75.8681996,
    "description": "Regional Rural Bank - Indore, Madhya Pradesh"
  },
  {
    "id": "bank_18",
    "name": "Himachal Pradesh Gramin Bank",
    "lat": 31.6516617,
    "lng": 77.0092542,
    "description": "Regional Rural Bank - Mandi, Himachal Pradesh"
  },
  {
    "id": "bank_19",
    "name": "Puducherry Grama Bank",
    "lat": 11.9340568,
    "lng": 79.8306447,
    "description": "Regional Rural Bank - Puducherry, Puducherry"
  },
  {
    "id": "bank_20",
    "name": "West Bengal Gramin Bank",
    "lat": 22.5736296,
    "lng": 88.3251045,
    "description": "Regional Rural Bank - Howrah, West Bengal"
  },
  {
    "id": "bank_21",
    "name": "Chhattisgarh Gramin Bank",
    "lat": 21.1610268,
    "lng": 81.7864412,
    "description": "Regional Rural Bank - Nava Raipur, Chhattisgarh"
  },
  {
    "id": "bank_22",
    "name": "Manipur Rural Bank",
    "lat": 24.7991162,
    "lng": 93.9364419,
    "description": "Regional Rural Bank - Imphal, Manipur"
  },
  {
    "id": "bank_23",
    "name": "Meghalaya Rural Bank",
    "lat": 25.5759931,
    "lng": 91.8827872,
    "description": "Regional Rural Bank - Shillong, Meghalaya"
  },
  {
    "id": "bank_24",
    "name": "J&K Grameen Bank",
    "lat": 32.7185614,
    "lng": 74.8580917,
    "description": "Regional Rural Bank - Jammu, Jammu & Kashmir"
  },
  {
    "id": "bank_25",
    "name": "Odisha Grameen Bank",
    "lat": 20.2602964,
    "lng": 85.8394521,
    "description": "Regional Rural Bank - Bhubaneshwar, Odisha"
  },
  {
    "id": "bank_26",
    "name": "Mizoram Rural Bank",
    "lat": 23.7277631,
    "lng": 92.7179947,
    "description": "Regional Rural Bank - Aizawl, Mizoram"
  },
  {
    "id": "bank_27",
    "name": "Indian Overseas Bank",
    "lat": 13.0836939,
    "lng": 80.270186,
    "description": "Public Sector Bank - Chennai, Tamil Nadu"
  },
  {
    "id": "bank_28",
    "name": "Bank of Baroda",
    "lat": 22.2973142,
    "lng": 73.1942567,
    "description": "Public Sector Bank - Vadodara, Gujarat"
  },
  {
    "id": "bank_29",
    "name": "Canara Bank",
    "lat": 12.9767936,
    "lng": 77.590082,
    "description": "Public Sector Bank - Bengaluru, Karnataka"
  },
  {
    "id": "bank_30",
    "name": "Punjab National Bank",
    "lat": 28.6138954,
    "lng": 77.2090057,
    "description": "Public Sector Bank - New Delhi, Delhi"
  },
  {
    "id": "bank_31",
    "name": "Punjab & Sind Bank",
    "lat": 28.6138954,
    "lng": 77.2090057,
    "description": "Public Sector Bank - New Delhi, Delhi"
  },
  {
    "id": "bank_32",
    "name": "Union Bank of India",
    "lat": 19.054999,
    "lng": 72.8692035,
    "description": "Public Sector Bank - Mumbai, Maharashtra"
  },
  {
    "id": "bank_33",
    "name": "Indian Bank",
    "lat": 13.0836939,
    "lng": 80.270186,
    "description": "Public Sector Bank - Chennai, Tamil Nadu"
  },
  {
    "id": "bank_34",
    "name": "Bank of Maharashtra",
    "lat": 18.5213738,
    "lng": 73.8545071,
    "description": "Public Sector Bank - Pune, Maharashtra"
  },
  {
    "id": "bank_35",
    "name": "Bank of India",
    "lat": 19.054999,
    "lng": 72.8692035,
    "description": "Public Sector Bank - Mumbai, Maharashtra"
  },
  {
    "id": "bank_36",
    "name": "Central bank Of India",
    "lat": 19.054999,
    "lng": 72.8692035,
    "description": "Public Sector Bank - Mumbai, Maharashtra"
  },
  {
    "id": "bank_37",
    "name": "UCO Bank",
    "lat": 22.5726459,
    "lng": 88.3638953,
    "description": "Public Sector Bank - Kolkata, West Bengal"
  },
  {
    "id": "bank_38",
    "name": "Assam North Eastern Development Finance Corporation Ltd. (NEDFi)",
    "lat": 26.1805978,
    "lng": 91.753943,
    "description": "Other Agency - Guwahati, Assam"
  },
  {
    "id": "bank_39",
    "name": "Jharkhand Silk Textile & Handicraft Development Corporation Ltd. (JHARCRAFT)",
    "lat": 23.3700501,
    "lng": 85.3250387,
    "description": "Other Agency - Ranchi, Jharkhand"
  },
  {
    "id": "bank_40",
    "name": "Small Industries Development Bank of India (SIDBI)",
    "lat": 26.8381,
    "lng": 80.9346001,
    "description": "Other Agency - Lucknow, Uttar Pradesh"
  },
  {
    "id": "bank_41",
    "name": "Shri Mahila Sewa Sahakari Bank Ltd.",
    "lat": 23.0215374,
    "lng": 72.5800568,
    "description": "Cooperative Society/Bank - Ahmedabad, Gujarat"
  },
  {
    "id": "bank_42",
    "name": "Konoklata mahila Urban Cooperative Bank",
    "lat": 26.4073841,
    "lng": 93.2551303,
    "description": "Cooperative Society/Bank - Assam"
  },
  {
    "id": "bank_43",
    "name": "Andhra Pradesh Scheduled Castes Cooperative Finance Corporation Ltd. (APSCCFC)",
    "lat": 16.5366119,
    "lng": 80.3810202,
    "description": "State Channelising Agency - Amaravathi, Andhra Pradesh"
  },
  {
    "id": "bank_44",
    "name": "Andhra Pradesh State Financial Corporation (APSFC)",
    "lat": 16.5115306,
    "lng": 80.6160469,
    "description": "State Channelising Agency - Vijayawada, Andhra Pradesh"
  },
  {
    "id": "bank_45",
    "name": "Assam State Development Corporation for SCs Ltd. (ASCDC)",
    "lat": 26.1805978,
    "lng": 91.753943,
    "description": "State Channelising Agency - Guwahati, Assam"
  },
  {
    "id": "bank_46",
    "name": "Bihar State SCs Co-operative Development Corporation Ltd. (BSSCCDC)",
    "lat": 25.6093239,
    "lng": 85.1235252,
    "description": "State Channelising Agency - Patna, Bihar"
  },
  {
    "id": "bank_47",
    "name": "Chandigarh SCs, BCs & Minorities Financial & Development Corporation Ltd. (CSCFDC)",
    "lat": 30.7334421,
    "lng": 76.7797143,
    "description": "State Channelising Agency - Chandigarh, Chandigarh"
  },
  {
    "id": "bank_48",
    "name": "Chhatisgarh State Antavasayee Sahkari Fin. & Dev.Corpn. (CGSCFDC)",
    "lat": 21.1610268,
    "lng": 81.7864412,
    "description": "State Channelising Agency - Naya Raipur, Chhattisgarh"
  },
  {
    "id": "bank_49",
    "name": "Dadra & Nagar Haveli, Daman & Diu SCs/STs/OBCs & Minorities Financial & Development Corporation (DNDSFDC)",
    "lat": 20.2736768,
    "lng": 73.0045787,
    "description": "State Channelising Agency - Silvassa, Dadra & Nagar Haveli, Daman & Diu"
  },
  {
    "id": "bank_50",
    "name": "Delhi SC/ST/OBC/Minorities & Handicapped Financial & Development Corporation (DSFDC)",
    "lat": 28.6664535,
    "lng": 77.2169781,
    "description": "State Channelising Agency - Delhi, Delhi"
  },
  {
    "id": "bank_51",
    "name": "Gujarat SCs Development Corporation (GSCDC)",
    "lat": 23.2232877,
    "lng": 72.6492267,
    "description": "State Channelising Agency - Gandhinagar, Gujarat"
  },
  {
    "id": "bank_52",
    "name": "Dr. Ambedkar Antyodaya Vikas Nigam (S.C.) (DAAVN)",
    "lat": 23.2232877,
    "lng": 72.6492267,
    "description": "State Channelising Agency - Gandhinagar, Gujarat"
  },
  {
    "id": "bank_53",
    "name": "Goa State SCs & OBCs Finance and Development Corporation Ltd. (GSCOBCDC)",
    "lat": 15.4989946,
    "lng": 73.8282141,
    "description": "State Channelising Agency - Panaji, Goa"
  },
  {
    "id": "bank_54",
    "name": "Haryana SCs Fin. and Development Corporation Ltd. (HSCDC)",
    "lat": 30.7573002,
    "lng": 76.8067372,
    "description": "State Channelising Agency - Chandigarh, Haryana"
  },
  {
    "id": "bank_55",
    "name": "Himachal Pradesh SCs & STs Development Corporation (HPSCSTDC)",
    "lat": 30.9077569,
    "lng": 77.1023645,
    "description": "State Channelising Agency - Solan, Himachal Pradesh"
  },
  {
    "id": "bank_56",
    "name": "Jharkhand State Scheduled Castes Cooperative Development Corporation (JSCDC)",
    "lat": 23.3700501,
    "lng": 85.3250387,
    "description": "State Channelising Agency - Ranchi, Jharkhand"
  },
  {
    "id": "bank_57",
    "name": "J&K SCs, STs & OBCs Dev. Corpn. Ltd. (JKSCSTBCDC)",
    "lat": 34.031181,
    "lng": 74.9047853,
    "description": "State Channelising Agency - Srinagar / Jammu, Jammu & Kashmir"
  },
  {
    "id": "bank_58",
    "name": "Dr B. R. Ambedkar Development Corporation Ltd. (DBRADC)",
    "lat": 12.9767936,
    "lng": 77.590082,
    "description": "State Channelising Agency - Bengaluru, Karnataka"
  },
  {
    "id": "bank_59",
    "name": "Kerala State Development Corporation for SCs & STs Ltd. (KSDC)",
    "lat": 10.5270099,
    "lng": 76.214621,
    "description": "State Channelising Agency - Thrissur, Kerala"
  },
  {
    "id": "bank_60",
    "name": "Kerala State Women's Development Corporation (KSWDC)",
    "lat": 8.4882267,
    "lng": 76.947551,
    "description": "State Channelising Agency - Thiruvananthapuram, Kerala"
  },
  {
    "id": "bank_61",
    "name": "MP State Cooperative SC Finance & Development Corporation (MPSCFDC)",
    "lat": 23.2584857,
    "lng": 77.401989,
    "description": "State Channelising Agency - Bhopal, Madhya Pradesh"
  },
  {
    "id": "bank_62",
    "name": "Mahatma Phule BCs Development Corporation Ltd. (MPBCDC)",
    "lat": 19.054999,
    "lng": 72.8692035,
    "description": "State Channelising Agency - Mumbai, Maharashtra"
  },
  {
    "id": "bank_63",
    "name": "Sahityaratna Lokshahir Annabhau Sathe Development Corporation Ltd. (SLASDC)",
    "lat": 19.054999,
    "lng": 72.8692035,
    "description": "State Channelising Agency - Mumbai, Maharashtra"
  },
  {
    "id": "bank_64",
    "name": "Sant Rohidas Leather Industries & Charmakar Development Corporation (LIDCOM)",
    "lat": 19.054999,
    "lng": 72.8692035,
    "description": "State Channelising Agency - Mumbai, Maharashtra"
  },
  {
    "id": "bank_65",
    "name": "Manipur Tribal Development Corporation Ltd. (MTDC)",
    "lat": 24.7991162,
    "lng": 93.9364419,
    "description": "State Channelising Agency - Imphal, Manipur"
  },
  {
    "id": "bank_66",
    "name": "Manipur SCs & STs Co-operative Dev. Bank (MSTCB)",
    "lat": 24.7991162,
    "lng": 93.9364419,
    "description": "State Channelising Agency - Imphal, Manipur"
  },
  {
    "id": "bank_67",
    "name": "Meghalaya Cooperative Apex Bank Ltd. (MCAB)",
    "lat": 25.5759931,
    "lng": 91.8827872,
    "description": "State Channelising Agency - Shillong, Meghalaya"
  },
  {
    "id": "bank_68",
    "name": "Mizoram Urban Cooperative Development Bank Ltd. (MUCO Bank)",
    "lat": 23.7277631,
    "lng": 92.7179947,
    "description": "State Channelising Agency - Aizawl, Mizoram"
  },
  {
    "id": "bank_69",
    "name": "Mizoram Khadi & Village Industries & Board (MKVIB)",
    "lat": 23.7277631,
    "lng": 92.7179947,
    "description": "State Channelising Agency - Aizawl, Mizoram"
  },
  {
    "id": "bank_70",
    "name": "Odisha SCs & STs Dev. Finance Co-op. Corpn. Ltd. (OSFDC)",
    "lat": 20.2602964,
    "lng": 85.8394521,
    "description": "State Channelising Agency - Bhubaneshwar, Odisha"
  },
  {
    "id": "bank_71",
    "name": "Puducherry Adi Dravidar Dev. Corpn. Ltd. (PADCO)",
    "lat": 11.9340568,
    "lng": 79.8306447,
    "description": "State Channelising Agency - Puducherry, Puducherry"
  },
  {
    "id": "bank_72",
    "name": "Punjab Scheduled Castes Land Development & Finance Corporation (PSCLDFC)",
    "lat": 30.7573002,
    "lng": 76.8067372,
    "description": "State Channelising Agency - Chandigarh, Punjab"
  },
  {
    "id": "bank_73",
    "name": "Rajasthan SCs & STs Fin. & Dev. Co-op. Corporation Ltd. (RSCDC)",
    "lat": 26.9154576,
    "lng": 75.8189817,
    "description": "State Channelising Agency - Jaipur, Rajasthan"
  },
  {
    "id": "bank_74",
    "name": "Sikkim Scheduled Castes Scheduled Tribes & Backward Classes Development Corporation (SSCSTBCDC)",
    "lat": 27.329046,
    "lng": 88.6122673,
    "description": "State Channelising Agency - Gangtok, Sikkim"
  },
  {
    "id": "bank_75",
    "name": "Tamil Nadu Adi Dravidar Housing & Development Corporation Ltd. (TAHDCO)",
    "lat": 13.0836939,
    "lng": 80.270186,
    "description": "State Channelising Agency - Chennai, Tamil Nadu"
  },
  {
    "id": "bank_76",
    "name": "Tripura Scheduled Castes Co-op. Devp. Corpn. Ltd. (TSCDC)",
    "lat": 23.8312377,
    "lng": 91.2823821,
    "description": "State Channelising Agency - Agartala, Tripura"
  },
  {
    "id": "bank_77",
    "name": "Uttarakhand Bahu-udeshiya Vitta Evam Vikas Nigam (UBVEVN)",
    "lat": 30.3255646,
    "lng": 78.0436813,
    "description": "State Channelising Agency - Dehradun, Uttarakhand"
  },
  {
    "id": "bank_78",
    "name": "UP Sahkari Gram Vikas Bank Ltd.",
    "lat": 26.8381,
    "lng": 80.9346001,
    "description": "State Channelising Agency - Lucknow, Uttar Pradesh"
  },
  {
    "id": "bank_79",
    "name": "UP Scheduled Castes Finance & Dev. Corpn. Ltd. (UPSCFDC)",
    "lat": 26.8381,
    "lng": 80.9346001,
    "description": "State Channelising Agency - Lucknow, Uttar Pradesh"
  },
  {
    "id": "bank_80",
    "name": "West Bengal SCs, STs & OBC Development & Finance Corporation (WBSCSTOBCDFC)",
    "lat": 22.5726459,
    "lng": 88.3638953,
    "description": "State Channelising Agency - Kolkata, West Bengal"
  }
]

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

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0  # Earth radius in km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (math.sin(dLat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@router.get("/pins")
def get_pins(lat: Optional[float] = None, lng: Optional[float] = None):
    """Retrieve all fixed SCA and partner bank pin locations, sorted by distance if user lat/lng provided."""
    pins = [pin.copy() for pin in PIN_DATASET]
    if lat is not None and lng is not None:
        for pin in pins:
            pin["distance"] = round(calculate_distance(lat, lng, pin["lat"], pin["lng"]), 2)
        pins.sort(key=lambda x: x.get("distance", 0) or 0)
    else:
        for pin in pins:
            pin["distance"] = None
    return pins

@router.get("/search")
async def search_location(q: str = Query(...)):
    """Search location via OpenStreetMap Nominatim API proxy."""
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={q}&limit=5"
    headers = {
        "Accept-Language": "en",
        "User-Agent": "YojanaAI-MapApp/1.0 (contact: admin@yojana.ai)"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10.0)
            if response.status_code == 200:
                return JSONResponse(content=response.json())
            return JSONResponse(content=[], status_code=response.status_code)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)

@router.get("/route")
async def get_route(start_lng: float, start_lat: float, end_lng: float, end_lat: float):
    """Calculate driving route via OSRM routing API proxy."""
    url = f"https://router.project-osrm.org/route/v1/driving/{start_lng},{start_lat};{end_lng},{end_lat}?overview=full&geometries=geojson"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                return JSONResponse(content=response.json())
            return JSONResponse(content={"error": "Routing failed"}, status_code=response.status_code)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)

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
