/* Check Eligibility Page Module */

let currentSelectedLoanType = 'Business';

function renderSkeletonProfileSummary() {
  const container = document.getElementById('eligibility-profile-summary');
  if (!container) return;
  container.innerHTML = `
    <div class="glass-panel profile-preload-card skeleton-card fade-in-up">
      <div class="profile-card-header">
        <div class="skeleton-box skeleton-title" style="width: 220px; height: 20px;"></div>
        <div class="skeleton-box skeleton-btn" style="width: 100px; height: 32px;"></div>
      </div>
      <div class="profile-info-grid">
        <div class="skeleton-box" style="height: 40px; border-radius: var(--radius-md);"></div>
        <div class="skeleton-box" style="height: 40px; border-radius: var(--radius-md);"></div>
        <div class="skeleton-box" style="height: 40px; border-radius: var(--radius-md);"></div>
        <div class="skeleton-box" style="height: 40px; border-radius: var(--radius-md);"></div>
      </div>
    </div>
  `;
}

async function initEligibilityForm() {
  renderSkeletonProfileSummary();
  // Preload user profile data
  const profile = await loadUserProfile();
  if (profile) {
    renderPreloadedProfileSummary(profile);
  }

  selectLoanType('Business');

  // Requirement 6: Prevent mouse-wheel scrolling from changing numerical input values
  preventNumberWheelScroll();
}

function preventNumberWheelScroll() {
  document.querySelectorAll('input[type="number"]').forEach(input => {
    input.addEventListener('wheel', function (e) {
      if (document.activeElement === this) {
        this.blur();
      }
    }, { passive: true });
  });
}

function renderPreloadedProfileSummary(profile) {
  const container = document.getElementById('eligibility-profile-summary');
  if (!container) return;

  container.innerHTML = `
    <div class="glass-panel profile-preload-card fade-in-up">
      <div class="profile-card-header">
        <div class="profile-card-title">
          <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
          Beneficiary Profile
        </div>
        <button class="btn btn-outline btn-sm" onclick="switchView('profile-view')">
          <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
          EDIT PROFILE
        </button>
      </div>

      <div class="profile-info-grid">
        <div class="profile-info-item">
          <span class="profile-info-label">Name</span>
          <span class="profile-info-value">${profile.name}</span>
        </div>
        <div class="profile-info-item">
          <span class="profile-info-label">Age / Gender</span>
          <span class="profile-info-value">${profile.age} Yrs / ${profile.gender}</span>
        </div>
        <div class="profile-info-item">
          <span class="profile-info-label">Beneficiary Status</span>
          <span class="profile-info-value" style="color: var(--emerald-600);">Verified Beneficiary</span>
        </div>
        <div class="profile-info-item">
          <span class="profile-info-label">Location</span>
          <span class="profile-info-value">${profile.area}, ${profile.district}, ${profile.state}</span>
        </div>
      </div>
    </div>
  `;
}

function selectLoanType(type) {
  currentSelectedLoanType = type;
  const bCard = document.getElementById('card-loan-business');
  const eCard = document.getElementById('card-loan-education');
  const bRadio = document.getElementById('radio-business');
  const eRadio = document.getElementById('radio-education');

  const bForm = document.getElementById('business-form-section');
  const eForm = document.getElementById('education-form-section');

  if (type === 'Business') {
    if (bCard) bCard.classList.add('selected');
    if (eCard) eCard.classList.remove('selected');
    if (bRadio) bRadio.checked = true;
    if (eRadio) eRadio.checked = false;

    if (bForm) bForm.style.display = 'block';
    if (eForm) eForm.style.display = 'none';

    document.getElementById('cost-field-label').innerText = 'Total Project / Unit Cost (₹)';
  } else {
    if (eCard) eCard.classList.add('selected');
    if (bCard) bCard.classList.remove('selected');
    if (eRadio) eRadio.checked = true;
    if (bRadio) bRadio.checked = false;

    if (eForm) eForm.style.display = 'block';
    if (bForm) bForm.style.display = 'none';

    document.getElementById('cost-field-label').innerText = 'Total Course Fees (₹)';
  }
}

async function handleCheckEligibilitySubmit(e) {
  if (e) e.preventDefault();

  const alertBox = document.getElementById('eligibility-error-alert');
  if (alertBox) alertBox.style.display = 'none';

  if (!currentUserProfile) {
    if (alertBox) {
      alertBox.innerText = 'Please complete your Beneficiary Profile first.';
      alertBox.style.display = 'flex';
    }
    switchView('profile-view');
    return;
  }

  // Requirement 5: Continuous accurate manual numerical input
  const incomeInput = document.getElementById('input-income').value.trim();
  const amountReqInput = document.getElementById('input-amount-req').value.trim();
  const costInput = document.getElementById('input-cost').value.trim();

  // FORM VALIDATION (A. Invalid Input)
  if (!incomeInput || !amountReqInput || !costInput) {
    if (alertBox) {
      alertBox.innerText = 'Please fill in all mandatory financial numerical fields.';
      alertBox.style.display = 'flex';
    }
    return;
  }

  const income = parseFloat(incomeInput);
  const amountReq = parseFloat(amountReqInput);
  const cost = parseFloat(costInput);

  if (isNaN(income) || income <= 0 || isNaN(amountReq) || amountReq <= 0 || isNaN(cost) || cost <= 0) {
    if (alertBox) {
      alertBox.innerText = 'Financial values must be positive numbers greater than zero.';
      alertBox.style.display = 'flex';
    }
    return;
  }

  let businessForm = null;
  let educationForm = null;

  if (currentSelectedLoanType === 'Business') {
    const purpose = document.getElementById('input-business-purpose').value.trim();
    const unit = document.getElementById('input-business-unit').value;
    const desc = document.getElementById('input-business-desc').value.trim();

    if (!purpose) {
      if (alertBox) {
        alertBox.innerText = 'Please specify the business purpose.';
        alertBox.style.display = 'flex';
      }
      return;
    }

    businessForm = { purpose, unit, description: desc };
  } else {
    const courseName = document.getElementById('input-course-name').value.trim();
    const collegeName = document.getElementById('input-college-name').value.trim();
    const yearsInput = document.getElementById('input-course-years').value.trim();

    if (!courseName || !collegeName || !yearsInput) {
      if (alertBox) {
        alertBox.innerText = 'Please provide course name, college name, and duration.';
        alertBox.style.display = 'flex';
      }
      return;
    }

    educationForm = { course_name: courseName, college_name: collegeName, number_of_years: parseInt(yearsInput) };
  }

  // Requirement 7: B. VALID INPUT BUT NO ELIGIBLE SCHEMES -> Allow submission to backend!
  const payload = {
    profile: {
      name: currentUserProfile.name,
      age: currentUserProfile.age,
      gender: currentUserProfile.gender,
      caste: "SC",
      area: currentUserProfile.area,
      district: currentUserProfile.district,
      state: currentUserProfile.state
    },
    annual_income: income,
    amount_required: amountReq,
    product_cost: cost,
    loan_type: currentSelectedLoanType === 'Business' ? 'Business Loan' : 'Education',
    business_form: businessForm,
    education_form: educationForm
  };

  const submitBtn = document.getElementById('btn-check-eligibility');
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="spinner"></span> Running Rule Engine...';

  try {
    const recResponse = await apiRequest('/eligibility/check', {
      method: 'POST',
      body: payload
    });

    // Render results view
    renderRecommendationResultsView(recResponse);
    switchView('recommendation-results-view');

  } catch (err) {
    if (alertBox) {
      alertBox.innerText = err.message || 'Failed to process eligibility determination.';
      alertBox.style.display = 'flex';
    }
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg> CHECK ELIGIBILITY';
  }
}
