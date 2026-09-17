/* Main Application Controller & Client-Side URL Hash Router */

const VIEW_ROUTES = {
  'schemes-view': '#/schemes',
  'scheme-detail-view': '#/schemes/',
  'eligibility-view': '#/eligibility',
  'recommendation-results-view': '#/recommendation',
  'emi-view': '#/emi',
  'geo-view': '#/geo',
  'profile-view': '#/profile'
};

document.addEventListener('DOMContentLoaded', () => {
  // Requirement 10: Authentication MUST NOT survive a browser page refresh.
  const navEntries = performance.getEntriesByType ? performance.getEntriesByType('navigation') : [];
  const isReload = (navEntries.length > 0 && navEntries[0].type === 'reload') || 
                 (performance.navigation && performance.navigation.type === 1);

  const token = getAuthToken();
  const userStr = sessionStorage.getItem('yojana_user');

  // If page was refreshed OR token/session is missing -> Force redirect to index.html for login
  if (isReload || !token || !userStr) {
    clearAuthSession();
    window.location.replace('login.html');
    return;
  }

  if (userStr) {
    const userObj = JSON.parse(userStr);
    const navName = document.getElementById('nav-user-name');
    const navAvatar = document.getElementById('nav-avatar-char');
    if (navName) navName.innerText = userObj.name || 'Beneficiary';
    if (navAvatar && userObj.name) navAvatar.innerText = userObj.name.charAt(0).toUpperCase();
  }

  // Pre-load User Profile
  loadUserProfile();

  // Listen to browser URL hash changes for separate endpoint navigation
  window.addEventListener('hashchange', handleHashRoute);

  // Initialize Route from URL hash or default to #/schemes
  handleHashRoute();
});

function handleHashRoute() {
  const hash = window.location.hash || '#/schemes';

  if (hash.startsWith('#/schemes/')) {
    const code = hash.replace('#/schemes/', '');
    if (code) {
      switchView('scheme-detail-view', { schemeCode: code }, false);
      return;
    }
  }

  switch (hash) {
    case '#/eligibility':
      switchView('eligibility-view', {}, false);
      break;
    case '#/recommendation':
      switchView('recommendation-results-view', {}, false);
      break;
    case '#/emi':
      switchView('emi-view', {}, false);
      break;
    case '#/geo':
      switchView('geo-view', {}, false);
      break;
    case '#/profile':
      switchView('profile-view', {}, false);
      break;
    case '#/schemes':
    default:
      switchView('schemes-view', {}, false);
      break;
  }
}

function switchView(viewId, params = {}, updateHash = true) {
  // Check auth before switching views
  const token = getAuthToken();
  if (!token) {
    clearAuthSession();
    window.location.replace('login.html');
    return;
  }

  // Synchronize URL Hash Endpoint if required
  if (updateHash && VIEW_ROUTES[viewId]) {
    if (viewId === 'scheme-detail-view' && params.schemeCode) {
      window.location.hash = `#/schemes/${params.schemeCode}`;
    } else {
      window.location.hash = VIEW_ROUTES[viewId];
    }
  }

  // Hide all view containers
  document.querySelectorAll('.app-view').forEach(v => {
    v.style.display = 'none';
    v.classList.remove('fade-in');
  });

  // Deactivate sidebar nav items
  document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));

  // Show target view
  const targetView = document.getElementById(viewId);
  if (targetView) {
    targetView.style.display = 'block';
    targetView.classList.add('fade-in');
  }

  // Highlight corresponding nav button or set title
  if (viewId === 'schemes-view') {
    const btn = document.getElementById('nav-btn-schemes');
    if (btn) btn.classList.add('active');
    document.getElementById('nav-page-title').innerText = 'All Schemes';
    renderAllSchemesPage('ALL');
  } else if (viewId === 'scheme-detail-view') {
    document.getElementById('nav-page-title').innerText = 'Scheme Details';
    if (params.schemeCode) {
      renderSchemeDetailPage(params.schemeCode);
    }
  } else if (viewId === 'profile-view') {
    document.getElementById('nav-page-title').innerText = 'Beneficiary Profile';
    renderFullProfilePage();
  } else if (viewId === 'eligibility-view') {
    const btn = document.getElementById('nav-btn-eligibility');
    if (btn) btn.classList.add('active');
    document.getElementById('nav-page-title').innerText = 'Check Eligibility';
    initEligibilityForm();
  } else if (viewId === 'emi-view') {
    const btn = document.getElementById('nav-btn-emi');
    if (btn) btn.classList.add('active');
    document.getElementById('nav-page-title').innerText = 'EMI Calculator';
    updateEmiCalculations();
  } else if (viewId === 'geo-view') {
    const btn = document.getElementById('nav-btn-geo');
    if (btn) btn.classList.add('active');
    document.getElementById('nav-page-title').innerText = 'Geo Locator';
    renderGeoLocatorPage('');
  } else if (viewId === 'recommendation-results-view') {
    document.getElementById('nav-page-title').innerText = 'Recommendation Results';
  }

  // Scroll smoothly to top of main container on view switch
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function handleLogout() {
  const token = getAuthToken();
  if (token) {
    apiRequest('/auth/logout', { method: 'POST' }).catch(() => {});
  }
  clearAuthSession();
  window.location.replace('login.html');
}
