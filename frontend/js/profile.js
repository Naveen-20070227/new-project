/* Full-Page Profile Management Module */

let currentUserProfile = null;
let isEditProfileMode = false;

async function loadUserProfile() {
  try {
    const profile = await apiRequest('/profile', { method: 'GET' });
    if (profile) {
      currentUserProfile = profile;
      updateNavbarProfileUI(profile);
    }
    return currentUserProfile;
  } catch (err) {
    console.log('Profile fetch notice:', err.message);
    return currentUserProfile;
  }
}

function updateNavbarProfileUI(profile) {
  if (!profile) return;
  const nameElem = document.getElementById('nav-user-name');
  const avatarElem = document.getElementById('nav-avatar-char');
  if (nameElem && profile.name) nameElem.innerText = profile.name;
  if (avatarElem && profile.name) avatarElem.innerText = profile.name.charAt(0).toUpperCase();
}

async function renderFullProfilePage() {
  const container = document.getElementById('profile-view-content');
  if (!container) return;

  const userStr = sessionStorage.getItem('yojana_user');
  const userObj = userStr ? JSON.parse(userStr) : {};

  // Build active profile from cache or session defaults
  const activeProfile = currentUserProfile || {
    name: userObj.name || 'Beneficiary',
    age: 28,
    gender: 'Male',
    caste: 'SC',
    area: 'Rural',
    district: 'District Office',
    state: 'State Office'
  };

  // RENDER IMMEDIATELY (Zero delay, no blank screen)
  if (isEditProfileMode) {
    renderProfileFormMode(container, activeProfile);
  } else {
    renderProfileReadOnlyMode(container, activeProfile, userObj.mobile || userObj.mobile_number);
  }

  // Render Latest Scheme Recommendation Section
  renderLatestRecommendationSection();

  // Background refresh from backend database
  const fresh = await loadUserProfile();
  if (fresh) {
    updateNavbarProfileUI(fresh);
    if (!isEditProfileMode) {
      renderProfileReadOnlyMode(container, fresh, userObj.mobile || userObj.mobile_number);
    }
  }
}

function renderProfileReadOnlyMode(container, profile, mobile) {
  const userStr = sessionStorage.getItem('yojana_user');
  const userObj = userStr ? JSON.parse(userStr) : {};
  const displayMobile = profile.mobile_number || mobile || userObj.mobile || userObj.mobile_number || 'Verified Mobile';

  const nameChar = (profile.name || userObj.name || 'B').charAt(0).toUpperCase();
  const distDisplay = (profile.district && profile.district !== 'District Office') ? profile.district : '<span style="color: var(--amber-500); font-weight: 500;">Click Edit Profile to set</span>';
  const stateDisplay = (profile.state && profile.state !== 'State Office') ? profile.state : '<span style="color: var(--amber-500); font-weight: 500;">Click Edit Profile to set</span>';

  container.innerHTML = `
    <div class="profile-header-card fade-in-up">
      <div class="profile-hero">
        <div class="profile-avatar-large">${nameChar}</div>
        <div class="profile-hero-info">
          <div class="profile-hero-name">${profile.name || userObj.name || 'Beneficiary'}</div>
          <div class="profile-hero-sub">
            <span class="badge badge-sc">Beneficiary</span>
            <span class="badge badge-eligible">OTP Verified</span>
            <span>Mobile: ${displayMobile}</span>
          </div>
        </div>

        <button class="btn btn-outline" onclick="toggleEditProfileMode(true)">
          <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
          Edit Profile
        </button>
      </div>

      <div class="profile-details-grid">
        <div class="profile-field-box">
          <span class="profile-field-label">Full Name</span>
          <span class="profile-field-value">${profile.name || userObj.name || 'Beneficiary'}</span>
        </div>

        <div class="profile-field-box">
          <span class="profile-field-label">Mobile Number</span>
          <span class="profile-field-value">${displayMobile}</span>
        </div>

        <div class="profile-field-box">
          <span class="profile-field-label">Age / Gender</span>
          <span class="profile-field-value">${profile.age || 28} Years / ${profile.gender || 'Male'}</span>
        </div>

        <div class="profile-field-box">
          <span class="profile-field-label">Beneficiary Category</span>
          <span class="profile-field-value" style="color: var(--primary-600);">Verified Beneficiary</span>
        </div>

        <div class="profile-field-box">
          <span class="profile-field-label">Area / Sector</span>
          <span class="profile-field-value">${profile.area || 'Rural'}</span>
        </div>

        <div class="profile-field-box">
          <span class="profile-field-label">District</span>
          <span class="profile-field-value">${distDisplay}</span>
        </div>

        <div class="profile-field-box">
          <span class="profile-field-label">State</span>
          <span class="profile-field-value">${stateDisplay}</span>
        </div>
      </div>
    </div>
  `;
}

function renderProfileFormMode(container, profile) {
  container.innerHTML = `
    <div class="glass-panel" style="padding: 32px; margin-bottom: 32px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; border-bottom: 1px solid var(--border-color); padding-bottom: 16px;">
        <h2 style="color: var(--text-main); font-size: 1.4rem;">Edit Beneficiary Profile</h2>
        <button class="btn btn-outline btn-sm" onclick="toggleEditProfileMode(false)">Cancel</button>
      </div>

      <div id="profile-save-error" class="alert alert-danger" style="display: none;"></div>

      <form onsubmit="handleSaveProfileForm(event)">
        <div class="form-group">
          <label class="form-label">Full Name <span class="req">*</span></label>
          <input type="text" id="edit-prof-name" class="form-control" value="${profile.name || ''}" required placeholder="Full Name as per Aadhaar">
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
          <div class="form-group">
            <label class="form-label">Age (Years) <span class="req">*</span></label>
            <input type="number" id="edit-prof-age" class="form-control" min="18" max="75" value="${profile.age || 28}" required>
          </div>

          <div class="form-group">
            <label class="form-label">Gender <span class="req">*</span></label>
            <select id="edit-prof-gender" class="form-select">
              <option value="Male" ${profile.gender === 'Male' ? 'selected' : ''}>Male</option>
              <option value="Female" ${profile.gender === 'Female' ? 'selected' : ''}>Female</option>
              <option value="Transgender" ${profile.gender === 'Transgender' ? 'selected' : ''}>Transgender</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Beneficiary Status</label>
          <div style="padding: 12px 16px; background: var(--emerald-50); border: 1px solid var(--border-emerald); border-radius: var(--radius-md); color: var(--emerald-700); font-weight: 700; display: flex; align-items: center; gap: 10px;">
            <input type="checkbox" checked disabled style="accent-color: var(--emerald-600); width: 18px; height: 18px;">
            <span>Verified Eligible Beneficiary</span>
          </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
          <div class="form-group">
            <label class="form-label">Area <span class="req">*</span></label>
            <select id="edit-prof-area" class="form-select">
              <option value="Rural" ${profile.area === 'Rural' ? 'selected' : ''}>Rural</option>
              <option value="Urban" ${profile.area === 'Urban' ? 'selected' : ''}>Urban</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">District <span class="req">*</span></label>
            <input type="text" id="edit-prof-district" class="form-control" value="${(profile.district && profile.district !== 'District Office') ? profile.district : ''}" required placeholder="e.g. Pune / Lucknow">
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">State <span class="req">*</span></label>
          <input type="text" id="edit-prof-state" class="form-control" value="${(profile.state && profile.state !== 'State Office') ? profile.state : ''}" required placeholder="e.g. Maharashtra / Uttar Pradesh">
        </div>

        <div style="display: flex; gap: 12px; margin-top: 10px;">
          <button type="submit" id="btn-save-profile" class="btn btn-emerald btn-full">
            Save & Update Profile
          </button>
        </div>
      </form>
    </div>
  `;
}

function toggleEditProfileMode(enable) {
  isEditProfileMode = enable;
  renderFullProfilePage();
}

async function handleSaveProfileForm(e) {
  if (e) e.preventDefault();
  const alertBox = document.getElementById('profile-save-error');
  if (alertBox) alertBox.style.display = 'none';

  const name = document.getElementById('edit-prof-name').value.trim();
  const age = parseInt(document.getElementById('edit-prof-age').value);
  const gender = document.getElementById('edit-prof-gender').value;
  const area = document.getElementById('edit-prof-area').value;
  const district = document.getElementById('edit-prof-district').value.trim();
  const state = document.getElementById('edit-prof-state').value.trim();

  try {
    const updated = await apiRequest('/profile', {
      method: 'POST',
      body: { name, age, gender, caste: 'SC', area, district, state }
    });
    currentUserProfile = updated;
    updateNavbarProfileUI(updated);
    isEditProfileMode = false;
    renderFullProfilePage();
  } catch (err) {
    if (alertBox) {
      alertBox.innerText = err.message || 'Failed to save profile.';
      alertBox.style.display = 'flex';
    }
  }
}

async function renderLatestRecommendationSection() {
  const container = document.getElementById('profile-latest-recommendation-container');
  if (!container) return;

  // Render skeleton card while fetching history
  container.innerHTML = `
    <div class="glass-panel skeleton-card fade-in-up" style="padding: 32px; margin-top: 32px; border-radius: var(--radius-xl);">
      <div class="skeleton-box skeleton-title" style="width: 260px; height: 24px; margin-bottom: 20px;"></div>
      <div class="skeleton-box skeleton-badge" style="width: 140px; margin-bottom: 16px;"></div>
      <div class="skeleton-box skeleton-title" style="width: 60%; height: 32px; margin-bottom: 20px;"></div>
      <div class="skeleton-box" style="width: 100%; height: 70px; border-radius: var(--radius-lg); margin-bottom: 24px;"></div>
      <div class="rec-features-grid">
        <div class="skeleton-box" style="height: 60px; border-radius: var(--radius-md);"></div>
        <div class="skeleton-box" style="height: 60px; border-radius: var(--radius-md);"></div>
        <div class="skeleton-box" style="height: 60px; border-radius: var(--radius-md);"></div>
        <div class="skeleton-box" style="height: 60px; border-radius: var(--radius-md);"></div>
      </div>
    </div>
  `;

  try {
    const history = await apiRequest('/recommendations/user/history', { method: 'GET' });

    if (!history || history.length === 0) {
      // Empty Recommendation Box
      container.innerHTML = `
        <div class="glass-panel fade-in-up" style="padding: 32px; text-align: center; margin-top: 32px;">
          <h3 style="font-size: 1.15rem; color: var(--text-main); margin-bottom: 12px;">Latest Scheme Recommendation</h3>
          <div style="padding: 40px; background: var(--bg-dark); border-radius: var(--radius-lg); border: 1px dashed var(--border-color);">
            <svg class="nav-icon" style="width: 42px; height: 42px; color: var(--text-dim); margin-bottom: 12px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
            <div style="font-size: 1rem; color: var(--text-main); font-weight: 600; margin-bottom: 6px;">No recommendation available yet</div>
            <div style="font-size: 0.88rem; color: var(--text-muted); margin-bottom: 16px;">Complete an eligibility check to receive a personalized scheme recommendation.</div>
            <button class="btn btn-emerald btn-sm" onclick="switchView('eligibility-view')">Check Eligibility Now</button>
          </div>
        </div>
      `;
      return;
    }

    // Latest recommendation entry
    const latest = history[0];
    const recs = latest.recommendations || [];
    const rank1 = recs.length > 0 ? recs[0] : null;
    const finalRec = latest.final_recommendation || {};
    const score = latest.rank_1_suitability_score || (rank1 ? rank1.suitability_score : 85);
    const schemeName = (rank1 && rank1.scheme_name) || finalRec.scheme_name || 'Recommended Scheme';

    const maxLoan = (rank1 && rank1.max_loan_desc) || 'Concessional Financing Available';
    const interestRate = (rank1 && rank1.interest_rate_desc) || 'Concessional Rate (4% - 6%)';
    const repayment = (rank1 && rank1.repayment_desc) || '3 - 5 Years Tenure';
    const moratorium = (rank1 && rank1.moratorium_desc) || 'Standard Moratorium Included';
    const whyList = (rank1 && rank1.why_recommended && rank1.why_recommended.length > 0)
      ? rank1.why_recommended
      : (finalRec.reason ? [finalRec.reason] : ['Matched based on applicant financial profile and scheme criteria.']);

    const formatMarkdown = (txt) => {
      if (!txt) return '';
      return txt
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>');
    };

    container.innerHTML = `
      <div style="margin-top: 36px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
        <div>
          <h2 style="font-size: 1.35rem; color: var(--text-main);">Latest Scheme Recommendation</h2>
          <p style="font-size: 0.85rem; color: var(--text-muted);">Last Evaluated: ${formatTimestamp(latest.created_at)}</p>
        </div>
        <button class="btn btn-outline btn-sm" onclick="switchView('eligibility-view')">
          + New Eligibility Check
        </button>
      </div>

      <!-- Hero Rank 1 Card (Exact UI match to Recommendation Results) -->
      <div class="hero-rec-card">
        <div class="hero-badge-ribbon">LATEST BEST MATCH</div>

        <h2 style="font-size: 1.6rem; color: var(--text-main); margin-bottom: 16px; padding-right: 140px;">${schemeName}</h2>

        <div class="score-display-box">
          <div class="score-circle">${score}</div>
          <div style="flex: 1;">
            <div style="display: flex; justify-content: space-between; font-size: 0.88rem; font-weight: 600; margin-bottom: 6px;">
              <span>Suitability Compatibility Score</span>
              <span style="color: var(--primary-600);">${score} / 100</span>
            </div>
            <div class="score-bar-bg">
              <div class="score-bar-fill" style="width: ${score}%;"></div>
            </div>
          </div>
        </div>

        <div class="rec-features-grid">
          <div class="rec-feature-item">
            <div class="rec-feature-title">Max Financing</div>
            <div class="rec-feature-val">${maxLoan}</div>
          </div>
          <div class="rec-feature-item">
            <div class="rec-feature-title">Interest Rate</div>
            <div class="rec-feature-val" style="color: var(--primary-600);">${interestRate}</div>
          </div>
          <div class="rec-feature-item">
            <div class="rec-feature-title">Repayment Period</div>
            <div class="rec-feature-val">${repayment}</div>
          </div>
          <div class="rec-feature-item">
            <div class="rec-feature-title">Moratorium</div>
            <div class="rec-feature-val">${moratorium}</div>
          </div>
        </div>

        <div style="margin-top: 24px;">
          <h4 style="color: var(--primary-600); font-size: 0.95rem; margin-bottom: 10px; display: flex; align-items: center; gap: 8px;">
            <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 20 11-18 0 9 9 0 0118 0z"></path></svg>
            Why This Scheme is Recommended
          </h4>
          <div class="rec-bullets-list">
            ${whyList.map(w => `
              <div class="bullet-item">
                <svg class="nav-icon bullet-icon-check" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                <span>${formatMarkdown(w)}</span>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `;

  } catch (err) {
    console.log('Error loading latest recommendation:', err);
  }
}
