/* All Schemes & Full-Page Scheme Detail Module with Skeleton Loading */

let cachedSchemes = [];

async function renderAllSchemesPage(filterCategory = 'ALL') {
  const container = document.getElementById('schemes-grid-container');
  if (!container) return;

  // Render 6 Skeleton Scheme Cards while loading data
  container.innerHTML = Array(6).fill(0).map(() => `
    <div class="skeleton-card">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span class="skeleton-box skeleton-title" style="width: 55%;"></span>
        <span class="skeleton-box skeleton-badge"></span>
      </div>
      <span class="skeleton-box skeleton-text"></span>
      <span class="skeleton-box skeleton-text-short"></span>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 8px 0;">
        <span class="skeleton-box skeleton-btn" style="height: 36px;"></span>
        <span class="skeleton-box skeleton-btn" style="height: 36px;"></span>
      </div>
      <span class="skeleton-box skeleton-btn"></span>
    </div>
  `).join('');

  try {
    if (cachedSchemes.length === 0) {
      cachedSchemes = await apiRequest('/schemes', { method: 'GET' });
    }

    let filtered = cachedSchemes;
    if (filterCategory !== 'ALL') {
      filtered = cachedSchemes.filter(s => s.category.toUpperCase() === filterCategory.toUpperCase());
    }

    if (filtered.length === 0) {
      container.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-muted);">No schemes found for selected category.</div>';
      return;
    }

    container.innerHTML = filtered.map(s => `
      <div class="glass-panel-interactive scheme-card fade-in-up">
        <div class="scheme-card-header">
          <h3 class="scheme-title">${s.name}</h3>
          <span class="badge ${s.category === 'Education' ? 'badge-info' : 'badge-sc'}">${s.category} Loan</span>
        </div>
        
        <p class="scheme-short-desc">${s.short_description}</p>
        
        <div class="scheme-meta-grid">
          <div>
            <div class="meta-item-label">Max Loan</div>
            <div class="meta-item-val">${s.max_loan_amount > 0 ? 'Up to ₹' + (s.max_loan_amount/100000).toFixed(2) + ' Lakh' : 'Up to 90%'}</div>
          </div>
          <div>
            <div class="meta-item-label">Interest Rate</div>
            <div class="meta-item-val">${s.beneficiary_interest_rate}% p.a.</div>
          </div>
        </div>

        <button class="btn btn-outline btn-full btn-sm" onclick="navigateToSchemeDetail('${s.code}')">
          <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 20 11-18 0 9 9 0 0118 0z"></path></svg>
          View Scheme Details
        </button>
      </div>
    `).join('');

  } catch (err) {
    container.innerHTML = `<div class="alert alert-danger" style="grid-column: 1/-1;">Error loading scheme database: ${err.message}</div>`;
  }
}

function filterSchemes(category) {
  document.querySelectorAll('.filter-chip').forEach(chip => chip.classList.remove('active'));
  const activeChip = document.getElementById(`filter-chip-${category.toLowerCase()}`);
  if (activeChip) activeChip.classList.add('active');
  renderAllSchemesPage(category);
}

function navigateToSchemeDetail(schemeCode) {
  switchView('scheme-detail-view', { schemeCode: schemeCode });
}

async function renderSchemeDetailPage(schemeCode) {
  const container = document.getElementById('scheme-detail-content');
  if (!container) return;

  // Render Full Scheme Detail Skeleton Loader
  container.innerHTML = `
    <div style="margin-bottom: 24px; display: flex; align-items: center; justify-content: space-between;">
      <span class="skeleton-box skeleton-badge" style="width: 140px;"></span>
      <span class="skeleton-box skeleton-badge" style="width: 110px;"></span>
    </div>
    <div class="glass-panel" style="padding: 36px; margin-bottom: 32px;">
      <span class="skeleton-box skeleton-title" style="width: 60%; height: 32px; margin-bottom: 16px;"></span>
      <span class="skeleton-box skeleton-text" style="margin-bottom: 8px;"></span>
      <span class="skeleton-box skeleton-text-short" style="margin-bottom: 32px;"></span>
      <div class="rec-features-grid" style="margin-bottom: 32px;">
        ${Array(6).fill(0).map(() => '<span class="skeleton-box skeleton-btn" style="height: 70px;"></span>').join('')}
      </div>
      <span class="skeleton-box skeleton-btn" style="height: 48px;"></span>
    </div>
  `;

  try {
    const scheme = await apiRequest(`/schemes/${schemeCode}`, { method: 'GET' });

    // Update top navbar page title to display the exact scheme name
    const pageTitleElem = document.getElementById('nav-page-title');
    if (pageTitleElem && scheme.name) {
      pageTitleElem.innerText = scheme.name;
    }

    container.innerHTML = `
      <div class="fade-in-up">
        <div style="margin-bottom: 24px; display: flex; align-items: center; justify-content: space-between;">
          <button class="btn btn-outline btn-sm" onclick="switchView('schemes-view')">
            ← Back to All Schemes
          </button>
          <div style="display: flex; align-items: center; gap: 8px;">
            <span class="badge badge-sc" style="font-size: 0.85rem; padding: 6px 12px;">CODE: ${scheme.code}</span>
            <span class="badge ${scheme.category === 'Education' ? 'badge-info' : 'badge-sc'}" style="font-size: 0.85rem; padding: 6px 12px;">${scheme.category} Scheme</span>
          </div>
        </div>

        <div class="glass-panel" style="padding: 36px; margin-bottom: 32px;">
          <div style="margin-bottom: 20px;">
            <div style="font-size: 0.8rem; color: var(--primary-600); text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; margin-bottom: 6px;">Official Scheme Details</div>
            <h1 style="font-size: 2rem; color: var(--text-main); font-weight: 800; margin-bottom: 12px; line-height: 1.25;">${scheme.name}</h1>
            <p style="font-size: 1.05rem; color: var(--text-body); line-height: 1.6;">${scheme.short_description}</p>
          </div>

          <h3 style="font-size: 1.15rem; color: var(--text-main); margin-bottom: 16px; border-bottom: 1px solid var(--border-color); padding-bottom: 10px;">Official Scheme Specifications</h3>

          <div class="rec-features-grid" style="margin-bottom: 32px;">
            <div class="rec-feature-item" style="padding: 18px;">
              <div class="rec-feature-title">Target Cost / Eligibility</div>
              <div class="rec-feature-val" style="font-size: 1rem; color: var(--emerald-600);">${scheme.target_cost_desc}</div>
            </div>

            <div class="rec-feature-item" style="padding: 18px;">
              <div class="rec-feature-title">Maximum Loan Limit</div>
              <div class="rec-feature-val" style="font-size: 1rem; color: var(--emerald-600);">${scheme.max_loan_amount > 0 ? 'Up to 90% (Max ₹' + scheme.max_loan_amount.toLocaleString('en-IN') + ')' : 'Up to 90% of cost'}</div>
            </div>

            <div class="rec-feature-item" style="padding: 18px;">
              <div class="rec-feature-title">Beneficiary Interest Rate</div>
              <div class="rec-feature-val" style="font-size: 1rem; color: var(--primary-600);">${scheme.beneficiary_interest_rate_desc}</div>
            </div>

            <div class="rec-feature-item" style="padding: 18px;">
              <div class="rec-feature-title">Repayment Period</div>
              <div class="rec-feature-val" style="font-size: 1rem;">${scheme.repayment_desc}</div>
            </div>

            <div class="rec-feature-item" style="padding: 18px;">
              <div class="rec-feature-title">Moratorium Period</div>
              <div class="rec-feature-val" style="font-size: 1rem;">${scheme.moratorium_desc}</div>
            </div>

            ${scheme.intermediary_rate ? `
              <div class="rec-feature-item" style="padding: 18px;">
                <div class="rec-feature-title">Intermediary Channel / SCA Rate</div>
                <div class="rec-feature-val" style="font-size: 1rem;">${scheme.intermediary_rate}</div>
              </div>
            ` : ''}
          </div>

          <div style="margin-bottom: 28px;">
            <h3 style="font-size: 1.15rem; color: var(--text-main); margin-bottom: 12px;">Detailed Scheme Overview</h3>
            <p style="font-size: 0.98rem; color: var(--text-body); line-height: 1.7;">${scheme.full_description}</p>
          </div>

          <div style="padding: 18px 20px; background: var(--bg-light-blue); border-radius: var(--radius-md); border: 1px solid var(--primary-100); display: flex; align-items: flex-start; gap: 12px;">
            <svg class="nav-icon" style="color: var(--primary-600); margin-top: 2px; flex-shrink: 0;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 20 11-18 0 9 9 0 0118 0z"></path></svg>
            <div>
              <div style="font-size: 0.9rem; color: var(--primary-700); font-weight: 700;">Government Channeling Agency Information</div>
              <div style="font-size: 0.88rem; color: var(--text-body); margin-top: 4px; line-height: 1.5;">Applications are processed via designated State Channelising Agencies (SCAs), Regional Rural Banks (RRBs), or Nationalized Banks. Visit the Geo Locator page for agency contact details in your state.</div>
            </div>
          </div>

          <div style="margin-top: 32px; text-align: center;">
            <button class="btn btn-primary btn-full" style="padding: 16px; font-size: 1.05rem;" onclick="switchView('eligibility-view')">
              Check Your Eligibility For ${scheme.name}
            </button>
          </div>
        </div>
      </div>
    `;

  } catch (err) {
    container.innerHTML = `<div class="alert alert-danger">Error loading scheme details: ${err.message}</div>`;
  }
}
