/* Geo Locator — Directory of State Channelising Agencies (SCAs) */

const SCA_DIRECTORY_FALLBACK = [
  {
    state: "Maharashtra",
    name: "Mahatma Phule Backward Class Development Corporation Ltd.",
    address: "Administrative Building, 4th Floor, Ramkrishna Chemburkar Marg, Chembur, Mumbai - 400071",
    phone: "022-25220803 / 25220804",
    website: "https://mpbcdc.maharashtra.gov.in"
  },
  {
    state: "Uttar Pradesh",
    name: "U.P. Scheduled Castes Finance & Development Corporation Ltd.",
    address: "TC-46/V-Vibhuti Khand, Gomti Nagar, Lucknow - 226010",
    phone: "0522-2307684 / 2307683",
    website: "http://upscfdc.up.gov.in"
  },
  {
    state: "Tamil Nadu",
    name: "Tamil Nadu Adi Dravidar Housing & Development Corporation (TAHDCO)",
    address: "No. 31, Cenotaph Road, 2nd Lane, Teynampet, Chennai - 600018",
    phone: "044-24310214 / 24310215",
    website: "https://tahdco.tn.gov.in"
  },
  {
    state: "Karnataka",
    name: "Dr. B.R. Ambedkar Development Corporation Ltd.",
    address: "9th Floor, Vishveshwaraiah Main Tower, Dr. B.R. Ambedkar Veedhi, Bengaluru - 560001",
    phone: "080-22864811 / 22864812",
    website: "https://adcl.karnataka.gov.in"
  },
  {
    state: "Punjab",
    name: "Punjab Scheduled Castes Land Development & Finance Corporation",
    address: "SCO 101-103, Sector 17-C, Chandigarh - 160017",
    phone: "0172-2704381 / 2704383",
    website: "http://pscldfc.punjab.gov.in"
  },
  {
    state: "Telangana",
    name: "Telangana Scheduled Castes Cooperative Development Corporation Ltd.",
    address: "DSS Bhavan, Masab Tank, Hyderabad - 500028",
    phone: "040-23391624 / 23391625",
    website: "https://tscorporation.telangana.gov.in"
  },
  {
    state: "Andhra Pradesh",
    name: "A.P. Scheduled Castes Co-op Finance Corporation Ltd.",
    address: "VC & MD Office, Tadepalli, Guntur District, Vijayawada - 520001",
    phone: "0866-2498222",
    website: "https://apscfc.ap.gov.in"
  },
  {
    state: "Delhi",
    name: "Delhi SC/ST/OBC/Minorities Development & Finance Corporation (DSFDC)",
    address: "2-3, Ambedkar Bhawan, Institutional Area, Sector-16, Rohini, New Delhi - 110089",
    phone: "011-27572701 / 27572702",
    website: "http://dsfdc.delhi.gov.in"
  },
  {
    state: "West Bengal",
    name: "West Bengal Scheduled Castes, Scheduled Tribes & OBC Development & Finance Corporation",
    address: "CF-217/A1, Sector-I, Salt Lake City, Kolkata - 700064",
    phone: "033-23348121 / 23348122",
    website: "http://wbscstdfc.gov.in"
  },
  {
    state: "Bihar",
    name: "Bihar State Scheduled Castes Co-operative Development Corporation Ltd.",
    address: "Maurya Lok Complex, Block A, 2nd Floor, Patna - 800001",
    phone: "0612-2215432",
    website: "http://scwelfare.bih.nic.in"
  },
  {
    state: "Gujarat",
    name: "Gujarat Scheduled Castes Development Corporation",
    address: "Block No. 14, 4th Floor, Dr. Jivraj Mehta Bhavan, Gandhinagar - 382010",
    phone: "079-23253724 / 23253725",
    website: "https://sje.gujarat.gov.in"
  },
  {
    state: "Madhya Pradesh",
    name: "M.P. State Scheduled Castes Finance & Development Corporation",
    address: "Rajiv Gandhi Bhawan, 35, Shyamla Hills, Bhopal - 462002",
    phone: "0755-2661582 / 2661583",
    website: "http://scwelfare.mp.gov.in"
  }
];

async function renderGeoLocatorPage(searchQuery = '') {
  const container = document.getElementById('geo-agencies-container');
  if (!container) return;

  const query = searchQuery.trim();
  let agencies = [];

  // Display skeleton agency cards while fetching
  container.innerHTML = Array(6).fill(0).map(() => `
    <div class="agency-card skeleton-card fade-in-up" style="pointer-events: none;">
      <div class="skeleton-box skeleton-badge" style="width: 100px; margin-bottom: 12px;"></div>
      <div class="skeleton-box skeleton-title" style="width: 80%; height: 22px; margin-bottom: 16px;"></div>
      <div class="skeleton-box skeleton-text" style="width: 90%; height: 16px; margin-bottom: 8px;"></div>
      <div class="skeleton-box skeleton-text" style="width: 70%; height: 16px; margin-bottom: 8px;"></div>
      <div class="skeleton-box skeleton-text" style="width: 50%; height: 16px;"></div>
    </div>
  `).join('');

  try {
    const url = query ? `/geo/agencies?search=${encodeURIComponent(query)}` : '/geo/agencies';
    const res = await apiRequest(url, { method: 'GET' });
    if (res && res.agencies) {
      agencies = res.agencies;
    }
  } catch (err) {
    const qLower = query.toLowerCase();
    agencies = SCA_DIRECTORY_FALLBACK.filter(item =>
      item.state.toLowerCase().includes(qLower) ||
      item.name.toLowerCase().includes(qLower) ||
      item.address.toLowerCase().includes(qLower)
    );
  }

  if (agencies.length === 0) {
    container.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 40px;">No State Channelising Agency offices found matching search criteria.</div>';
    return;
  }

  container.innerHTML = agencies.map(item => `
    <div class="agency-card fade-in-up">
      <span class="agency-state-badge">${item.state}</span>
      <h3 class="agency-name">${item.name}</h3>
      <div class="agency-contact-info">
        <div><strong>Address:</strong> ${item.address}</div>
        <div><strong>Helpline Phone:</strong> ${item.phone}</div>
        <div><strong>Official Portal:</strong> <a href="${item.website}" target="_blank" style="color: var(--primary-600); text-decoration: underline;">Visit Portal</a></div>
      </div>
    </div>
  `).join('');
}
