/* EMI Calculator Module with Dedicated API Endpoint Integration */

async function updateEmiCalculations() {
  const amount = parseFloat(document.getElementById('emi-amount-slider').value);
  const rate = parseFloat(document.getElementById('emi-rate-slider').value);
  const years = parseFloat(document.getElementById('emi-tenure-slider').value);

  document.getElementById('val-emi-amount').innerText = '₹' + amount.toLocaleString('en-IN');
  document.getElementById('val-emi-rate').innerText = rate.toFixed(1) + '%';
  document.getElementById('val-emi-tenure').innerText = years + (years === 1 ? ' Year' : ' Years');

  // Immediate Client Math for Instant Slider Responsiveness
  const monthlyRate = rate / 12 / 100;
  const totalMonths = years * 12;

  let emiMonthly = 0;
  if (monthlyRate > 0) {
    emiMonthly = (amount * monthlyRate * Math.pow(1 + monthlyRate, totalMonths)) / (Math.pow(1 + monthlyRate, totalMonths) - 1);
  } else {
    emiMonthly = amount / totalMonths;
  }

  const emiQuarterly = emiMonthly * 3;
  const totalPayment = emiMonthly * totalMonths;
  const totalInterest = totalPayment - amount;

  document.getElementById('res-emi-monthly').innerText = '₹' + Math.round(emiMonthly).toLocaleString('en-IN');
  document.getElementById('res-emi-quarterly').innerText = '₹' + Math.round(emiQuarterly).toLocaleString('en-IN');
  document.getElementById('res-total-interest').innerText = '₹' + Math.round(totalInterest).toLocaleString('en-IN');
  document.getElementById('res-total-payment').innerText = '₹' + Math.round(totalPayment).toLocaleString('en-IN');

  // Fetch precise values from Dedicated Backend API Endpoint /api/emi/calculate
  try {
    const apiRes = await apiRequest(`/emi/calculate?amount=${amount}&rate=${rate}&tenure_years=${years}`, { method: 'GET' });
    if (apiRes) {
      document.getElementById('res-emi-monthly').innerText = '₹' + Math.round(apiRes.monthly_instalment).toLocaleString('en-IN');
      document.getElementById('res-emi-quarterly').innerText = '₹' + Math.round(apiRes.quarterly_instalment).toLocaleString('en-IN');
      document.getElementById('res-total-interest').innerText = '₹' + Math.round(apiRes.total_interest).toLocaleString('en-IN');
      document.getElementById('res-total-payment').innerText = '₹' + Math.round(apiRes.total_payment).toLocaleString('en-IN');
    }
  } catch (err) {
    // Client math fallback active
  }
}
