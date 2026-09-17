/* Recommendation Results UI Component */

function renderRecommendationResultsView(data) {
  const container = document.getElementById('recommendation-results-content');
  if (!container) return;

  const appSum = data.applicant_summary;
  const eligStatus = data.eligibility_status;
  const recs = data.recommendations || [];
  const finalRec = data.final_recommendation || {};

  const formatCurrency = (val) => '₹' + parseFloat(val).toLocaleString('en-IN', { maximumFractionDigits: 2 });
  const formatMarkdown = (txt) => {
    if (!txt) return '';
    return txt
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n\n/g, '<br><br>')
      .replace(/\n/g, '<br>');
  };

  let html = `
    <!-- Top Summary Banner -->
    <div class="rec-header-summary fade-in-up">
      <div class="summary-chip">
        <div class="summary-chip-label">Applicant</div>
        <div class="summary-chip-val" style="color: var(--text-main); font-size: 1rem;">${appSum.name}</div>
        <div style="font-size: 0.78rem; color: var(--emerald-600); font-weight: 600;">Verified Beneficiary</div>
      </div>
      <div class="summary-chip">
        <div class="summary-chip-label">Category</div>
        <div class="summary-chip-val" style="color: var(--text-main); font-size: 1rem;">${appSum.loan_type}</div>
        <div style="font-size: 0.78rem; color: var(--text-muted);">${appSum.specifics.purpose || appSum.specifics.course_name || 'General'}</div>
      </div>
      <div class="summary-chip">
        <div class="summary-chip-label">Required Amount</div>
        <div class="summary-chip-val">${formatCurrency(appSum.amount_required)}</div>
        <div style="font-size: 0.78rem; color: var(--text-dim);">Cost: ${formatCurrency(appSum.product_cost)}</div>
      </div>
      <div class="summary-chip">
        <div class="summary-chip-label">Annual Income</div>
        <div class="summary-chip-val" style="color: var(--amber-500);">${formatCurrency(appSum.annual_income)}</div>
        <div style="font-size: 0.78rem; color: var(--text-dim);">${appSum.area}, ${appSum.district}</div>
      </div>
    </div>
  `;

  // REQUIREMENT 7: ZERO ELIGIBLE SCHEMES HANDLING
  const eligibleCount = eligStatus.eligible ? eligStatus.eligible.length : 0;

  if (eligibleCount === 0) {
    html += `
      <div class="alert alert-danger" style="padding: 24px; margin-bottom: 28px;">
        <div style="font-size: 1.15rem; font-weight: 700; color: var(--rose-600); margin-bottom: 8px;">
          You are not eligible for any of the available schemes based on the information provided.
        </div>
        <div style="font-size: 0.9rem; color: var(--text-main);">
          The rule-based eligibility engine evaluated all official government schemes against your project cost, loan required, and category parameters. None met full eligibility.
        </div>
      </div>

      <div class="status-section">
        <h3 style="color: var(--text-main); font-size: 1.15rem; margin-bottom: 16px;">Scheme Eligibility Breakdown & Specific Reasons</h3>
        
        <div style="display: flex; flex-direction: column; gap: 16px;">
          ${(eligStatus.ineligible || []).map(scheme => `
            <div class="glass-panel" style="padding: 20px; border-left: 4px solid var(--rose-600);">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h4 style="font-size: 1.05rem; color: var(--text-main);">${scheme.scheme_name}</h4>
                <span class="badge badge-ineligible">NOT ELIGIBLE</span>
              </div>
              <div style="display: flex; flex-direction: column; gap: 6px;">
                ${scheme.reasons.map(r => `<div class="reason-bullet" style="color: var(--rose-text);">✗ ${r}</div>`).join('')}
              </div>
            </div>
          `).join('')}
        </div>
      </div>

      <div class="disclaimer-box" style="margin-top: 32px;">
        <strong>OFFICIAL DISCLAIMER:</strong> ${data.disclaimer}
      </div>
    `;

    container.innerHTML = html;
    return;
  }

  // AI Explanation Banner (when eligible schemes exist)
  if (!data.ai_available && data.ai_error_message) {
    html += `
      <div class="alert alert-warning">
        <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
        <div>
          <strong>AI Status Notice:</strong> ${data.ai_error_message}<br>
          <span style="font-size: 0.84rem;">Determined using deterministic Rule-Based Eligibility Engine & Objective Compatibility Scoring.</span>
        </div>
      </div>
    `;
  } else {
    html += `
      <div class="alert alert-success" style="align-items: flex-start; padding: 20px 22px;">
        <svg class="nav-icon" style="margin-top: 2px; flex-shrink: 0;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
        <div>
          <strong style="color: var(--emerald-700); font-size: 1rem; display: block; margin-bottom: 8px;">AI Executive Recommendation & Suitability Explanation</strong>
          <div style="font-size: 0.95rem; color: var(--text-main); line-height: 1.6; font-weight: 400;">
            ${formatMarkdown(finalRec.reason) || 'Optimal scheme recommendation determined based on eligibility rules and suitability analysis.'}
          </div>
        </div>
      </div>
    `;
  }

  // Recommendations Display (Rank 1, Rank 2, Rank 3)
  if (recs.length > 0) {
    const rank1 = recs[0];

    html += `
      <div style="margin-bottom: 24px;">
        <h2 style="color: var(--text-main); font-size: 1.35rem; display: flex; align-items: center; gap: 10px;">
          Best Recommended Scheme
        </h2>
      </div>

      <!-- Hero Rank 1 Card -->
      <div class="hero-rec-card fade-in-up">
        <div class="hero-badge-ribbon">RANK 1 — BEST MATCH</div>

        <h2 style="font-size: 1.6rem; color: var(--text-main); margin-bottom: 16px;">${rank1.scheme_name}</h2>

        <div class="score-display-box">
          <div class="score-circle">${rank1.suitability_score}</div>
          <div style="flex: 1;">
            <div style="display: flex; justify-content: space-between; font-size: 0.88rem; font-weight: 600; margin-bottom: 6px;">
              <span>Suitability Compatibility Score</span>
              <span style="color: var(--primary-600);">${rank1.suitability_score} / 100</span>
            </div>
            <div class="score-bar-bg">
              <div class="score-bar-fill" style="width: ${rank1.suitability_score}%;"></div>
            </div>
          </div>
        </div>

        <div class="rec-features-grid">
          <div class="rec-feature-item">
            <div class="rec-feature-title">Max Financing</div>
            <div class="rec-feature-val">${rank1.max_loan_desc}</div>
          </div>
          <div class="rec-feature-item">
            <div class="rec-feature-title">Interest Rate</div>
            <div class="rec-feature-val" style="color: var(--primary-600);">${rank1.interest_rate_desc}</div>
          </div>
          <div class="rec-feature-item">
            <div class="rec-feature-title">Repayment Period</div>
            <div class="rec-feature-val">${rank1.repayment_desc}</div>
          </div>
          <div class="rec-feature-item">
            <div class="rec-feature-title">Moratorium</div>
            <div class="rec-feature-val">${rank1.moratorium_desc}</div>
          </div>
        </div>

        <div style="margin-top: 24px;">
          <h4 style="color: var(--primary-600); font-size: 0.95rem; margin-bottom: 10px; display: flex; align-items: center; gap: 8px;">
            <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 20 11-18 0 9 9 0 0118 0z"></path></svg>
            Why This Scheme is Recommended
          </h4>
          <div class="rec-bullets-list">
            ${rank1.why_recommended.map(w => `
              <div class="bullet-item">
                <svg class="nav-icon bullet-icon-check" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                <span>${w}</span>
              </div>
            `).join('')}
          </div>
        </div>

        ${rank1.important_conditions && rank1.important_conditions.length > 0 ? `
          <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border-color);">
            <h4 style="color: var(--amber-500); font-size: 0.9rem; margin-bottom: 8px;">Important Conditions & Guidelines</h4>
            <ul style="padding-left: 20px; font-size: 0.85rem; color: var(--text-muted);">
              ${rank1.important_conditions.map(c => `<li>${c}</li>`).join('')}
            </ul>
          </div>
        ` : ''}
      </div>
    `;

    // Alternatives (Rank 2 & Rank 3)
    if (recs.length > 1) {
      html += `<h3 class="alt-recs-title">Alternative Eligible Schemes</h3>`;
      for (let i = 1; i < recs.length; i++) {
        const alt = recs[i];
        html += `
          <div class="alt-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
              <div>
                <span class="badge badge-info" style="margin-bottom: 6px;">RANK ${alt.rank} — ALTERNATIVE</span>
                <h3 style="font-size: 1.25rem; color: var(--text-main);">${alt.scheme_name}</h3>
              </div>
              <div style="text-align: right;">
                <div style="font-size: 0.75rem; color: var(--text-dim);">Suitability Score</div>
                <div style="font-size: 1.2rem; font-weight: 800; color: var(--amber-500);">${alt.suitability_score} / 100</div>
              </div>
            </div>

            <div class="rec-features-grid" style="margin: 14px 0;">
              <div class="rec-feature-item">
                <div class="rec-feature-title">Max Financing</div>
                <div class="rec-feature-val" style="font-size: 0.85rem;">${alt.max_loan_desc}</div>
              </div>
              <div class="rec-feature-item">
                <div class="rec-feature-title">Interest Rate</div>
                <div class="rec-feature-val" style="font-size: 0.85rem;">${alt.interest_rate_desc}</div>
              </div>
              <div class="rec-feature-item">
                <div class="rec-feature-title">Repayment</div>
                <div class="rec-feature-val" style="font-size: 0.85rem;">${alt.repayment_desc}</div>
              </div>
            </div>

            <div class="rec-bullets-list">
              ${alt.why_recommended.map(w => `
                <div class="bullet-item" style="font-size: 0.88rem;">
                  <svg class="nav-icon bullet-icon-check" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                  <span>${w}</span>
                </div>
              `).join('')}
            </div>
          </div>
        `;
      }
    }
  }

  // Rule-Based Eligibility Status Breakdown
  html += `
    <div class="status-section">
      <h3 style="color: var(--text-main); font-size: 1.15rem; margin-bottom: 12px;">Rule-Based Eligibility Breakdown</h3>
      <div class="status-grid">
        <div class="status-card eligible">
          <div class="status-card-title" style="color: var(--emerald-700);">
            <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 20 11-18 0 9 9 0 0118 0z"></path></svg>
            Eligible Schemes (${eligibleCount})
          </div>
          ${eligStatus.eligible.map(e => `
            <div style="font-weight: 600; color: var(--text-main); margin-top: 10px;">${e.scheme_name}</div>
            ${e.reasons.map(r => `<div class="reason-bullet" style="color: var(--emerald-700);">✓ ${r}</div>`).join('')}
          `).join('')}
        </div>

        <div class="status-card ineligible">
          <div class="status-card-title" style="color: var(--rose-600);">
            <svg class="nav-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 20 11-18 0 9 9 0 0118 0z"></path></svg>
            Ineligible Schemes (${eligStatus.ineligible ? eligStatus.ineligible.length : 0})
          </div>
          ${(eligStatus.ineligible && eligStatus.ineligible.length > 0) ? eligStatus.ineligible.map(e => `
            <div style="font-weight: 600; color: var(--text-main); margin-top: 10px;">${e.scheme_name}</div>
            ${e.reasons.map(r => `<div class="reason-bullet" style="color: var(--rose-text);">✗ ${r}</div>`).join('')}
          `).join('') : '<div style="font-size: 0.85rem; color: var(--text-dim); margin-top: 8px;">None</div>'}
        </div>
      </div>
    </div>
  `;

  // Official Disclaimer
  html += `
    <div class="disclaimer-box">
      <strong>OFFICIAL DISCLAIMER:</strong> ${data.disclaimer}
    </div>
  `;

  container.innerHTML = html;
}
