/* New NSFDC Scheme-Driven EMI Calculator Module */

let emiSchemes = [];
let selectedEmiScheme = null;
let calcDebounceTimeout = null;

async function initEmiCalculator() {
  await loadEmiSchemes();
  setupEmiEventListeners();
  updateSliderBackgrounds();
}

async function loadEmiSchemes() {
  try {
    const res = await apiRequest('/emi/schemes', { method: 'GET' });
    if (res && Array.isArray(res) && res.length > 0) {
      emiSchemes = res;
    } else {
      fallbackEmiSchemes();
    }
  } catch (e) {
    fallbackEmiSchemes();
  }
  initEmiDropdown();
}

function fallbackEmiSchemes() {
  emiSchemes = [
    { id: 'SCHEME_001', name: 'Micro Finance Scheme (MFS)', rate: 6.5 },
    { id: 'SCHEME_002', name: 'Term Loan', rate: 8.0 },
    { id: 'SCHEME_003', name: 'Aajeevika Micro-Finance', rate: 15.0 },
    { id: 'SCHEME_004_1', name: 'Udyam Nidhi (Cooperative)', rate: 13.0 },
    { id: 'SCHEME_004_2', name: 'Udyam Nidhi (SFBs)', rate: 15.0 },
    { id: 'SCHEME_005', name: 'Educational Loan Scheme', rate: 6.5 }
  ];
}

function initEmiDropdown() {
  const dropdownOptions = document.getElementById('dropdownOptions');
  const dropdownSelected = document.getElementById('dropdownSelected');
  const dropdown = document.getElementById('schemeDropdown');

  if (!dropdownOptions || !dropdownSelected || !dropdown) return;

  dropdownOptions.innerHTML = '';

  // Deduplicate schemes by ID / Name
  const uniqueSchemes = [];
  const seen = new Set();
  emiSchemes.forEach(scheme => {
    const key = scheme.id || scheme.name;
    if (!seen.has(key)) {
      seen.add(key);
      uniqueSchemes.push(scheme);
    }
  });
  emiSchemes = uniqueSchemes;

  emiSchemes.forEach(scheme => {
    const option = document.createElement('div');
    option.classList.add('dropdown-option');
    option.textContent = scheme.name;
    option.addEventListener('click', (e) => {
      e.stopPropagation();
      selectEmiScheme(scheme);
      dropdown.classList.remove('active');
    });
    dropdownOptions.appendChild(option);
  });

  dropdownSelected.onclick = (e) => {
    dropdown.classList.toggle('active');
    e.stopPropagation();
  };

  document.onclick = () => {
    dropdown.classList.remove('active');
  };

  if (emiSchemes.length > 0 && !selectedEmiScheme) {
    selectEmiScheme(emiSchemes[0]);
  }
}

function selectEmiScheme(scheme) {
  selectedEmiScheme = scheme;
  const dropdownSelected = document.getElementById('dropdownSelected');
  const interestInput = document.getElementById('interestInput');
  const interestSlider = document.getElementById('interestSlider');

  if (dropdownSelected) {
    const span = dropdownSelected.querySelector('span');
    if (span) {
      span.textContent = scheme.name;
      span.style.color = '#0c1a4b';
    }
  }

  if (interestInput) interestInput.value = scheme.rate;
  if (interestSlider) interestSlider.value = scheme.rate;

  calculateEMI();
}

function formatEmiCurrency(num) {
  return '₹ ' + Math.round(num).toLocaleString('en-IN');
}

function parseEmiCurrency(str) {
  return Number(String(str).replace(/,/g, ''));
}

function syncAmount(fromSlider = false) {
  const amountSlider = document.getElementById('amountSlider');
  const amountInput = document.getElementById('amountInput');
  if (!amountSlider || !amountInput) return;

  let val;
  if (fromSlider) {
    val = amountSlider.value;
    amountInput.value = Number(val).toLocaleString('en-IN');
  } else {
    val = parseEmiCurrency(amountInput.value);
    if (isNaN(val) || val < 10000) val = 10000;
    if (val > 5000000) val = 5000000;
    amountSlider.value = val;
    amountInput.value = val.toLocaleString('en-IN');
  }
  calculateEMI();
}

function syncTenure(fromSlider = false) {
  const tenureSlider = document.getElementById('tenureSlider');
  const tenureInput = document.getElementById('tenureInput');
  const tenureType = document.getElementById('tenureType');
  if (!tenureSlider || !tenureInput || !tenureType) return;

  let val;
  if (fromSlider) {
    val = tenureSlider.value;
    tenureInput.value = val;
  } else {
    val = parseInt(tenureInput.value);
    if (isNaN(val) || val < 1) val = 1;
    const max = tenureType.value === 'years' ? 30 : 144;
    if (val > max) val = max;
    tenureSlider.value = val;
    tenureInput.value = val;
  }
  calculateEMI();
}

function handleTenureTypeChange() {
  const tenureSlider = document.getElementById('tenureSlider');
  const tenureInput = document.getElementById('tenureInput');
  const tenureType = document.getElementById('tenureType');
  if (!tenureSlider || !tenureInput || !tenureType) return;

  if (tenureType.value === 'years') {
    tenureSlider.max = 30;
    let currentMonths = parseInt(tenureSlider.value);
    let years = Math.max(1, Math.round(currentMonths / 12));
    tenureSlider.value = years;
    tenureInput.value = years;
  } else {
    tenureSlider.max = 144;
    let currentYears = parseInt(tenureSlider.value);
    let months = currentYears * 12;
    tenureSlider.value = months;
    tenureInput.value = months;
  }
  calculateEMI();
}

async function calculateEMI() {
  const amountInput = document.getElementById('amountInput');
  const interestInput = document.getElementById('interestInput');
  const tenureInput = document.getElementById('tenureInput');
  const tenureType = document.getElementById('tenureType');
  const emiValue = document.getElementById('emiValue');
  const totalInterestValue = document.getElementById('totalInterestValue');
  const totalPayableValue = document.getElementById('totalPayableValue');

  if (!amountInput || !interestInput || !tenureInput || !tenureType) return;

  let principal = parseEmiCurrency(amountInput.value);
  let rate = parseFloat(interestInput.value);
  let tenure = parseInt(tenureInput.value);
  let tType = tenureType.value;

  if (!principal || !rate || !tenure) {
    if (emiValue) emiValue.textContent = '₹ 0';
    if (totalInterestValue) totalInterestValue.textContent = '₹ 0';
    if (totalPayableValue) totalPayableValue.textContent = '₹ 0';
    return;
  }

  // Instant local math calculation for smooth UI response
  let tenureInMonths = tType === 'years' ? tenure * 12 : tenure;
  let r = rate / 12 / 100;
  let n = tenureInMonths;
  let emi = rate === 0 ? principal / n : (principal * r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1);
  let totalPayable = emi * n;
  let totalInterest = totalPayable - principal;

  if (emiValue) emiValue.textContent = formatEmiCurrency(emi);
  if (totalInterestValue) totalInterestValue.textContent = formatEmiCurrency(totalInterest);
  if (totalPayableValue) totalPayableValue.textContent = formatEmiCurrency(totalPayable);

  updateSliderBackgrounds();

  // Call API for exact server calculations
  if (calcDebounceTimeout) clearTimeout(calcDebounceTimeout);
  calcDebounceTimeout = setTimeout(async () => {
    try {
      const res = await apiRequest('/emi/calculate', {
        method: 'POST',
        body: {
          principal: principal,
          rate: rate,
          tenure: tenure,
          tenure_type: tType,
          scheme_id: selectedEmiScheme ? selectedEmiScheme.id : null
        }
      });
      if (res) {
        if (emiValue) emiValue.textContent = res.formatted_emi || formatEmiCurrency(res.monthly_emi);
        if (totalInterestValue) totalInterestValue.textContent = res.formatted_interest || formatEmiCurrency(res.total_interest);
        if (totalPayableValue) totalPayableValue.textContent = res.formatted_payable || formatEmiCurrency(res.total_payable);
      }
    } catch (e) {
      // Local math fallback is active
    }
  }, 50);
}

function updateSliderBackgrounds() {
  const amountSlider = document.getElementById('amountSlider');
  const interestSlider = document.getElementById('interestSlider');
  const tenureSlider = document.getElementById('tenureSlider');

  [amountSlider, interestSlider, tenureSlider].forEach(slider => {
    if (slider) {
      const val = (slider.value - slider.min) / (slider.max - slider.min) * 100;
      slider.style.background = `linear-gradient(to right, #2563eb ${val}%, #c3d7f9 ${val}%)`;
    }
  });
}

function setupEmiEventListeners() {
  const amountSlider = document.getElementById('amountSlider');
  const amountInput = document.getElementById('amountInput');
  const tenureSlider = document.getElementById('tenureSlider');
  const tenureInput = document.getElementById('tenureInput');
  const tenureType = document.getElementById('tenureType');

  if (amountSlider) amountSlider.oninput = () => { syncAmount(true); updateSliderBackgrounds(); };
  if (amountInput) amountInput.onchange = () => { syncAmount(false); updateSliderBackgrounds(); };

  if (tenureSlider) tenureSlider.oninput = () => { syncTenure(true); updateSliderBackgrounds(); };
  if (tenureInput) tenureInput.onchange = () => { syncTenure(false); updateSliderBackgrounds(); };
  if (tenureType) tenureType.onchange = handleTenureTypeChange;
}

// Alias function for compatibility with app.js switchView
function updateEmiCalculations() {
  initEmiCalculator();
}
