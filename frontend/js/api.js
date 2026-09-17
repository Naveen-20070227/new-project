/* Centralized API Client with Refresh-Loss Session Token Handling */

const API_BASE = '/api';

// In-Memory & Session Storage (Cleared on Page Refresh per Requirement 10)
function getAuthToken() {
  return sessionStorage.getItem('yojana_token');
}

function setAuthToken(token, userObj) {
  sessionStorage.setItem('yojana_token', token);
  sessionStorage.setItem('yojana_user', JSON.stringify(userObj));
}

function clearAuthSession() {
  sessionStorage.removeItem('yojana_token');
  sessionStorage.removeItem('yojana_user');
}

function getAuthHeaders() {
  const token = getAuthToken();
  const headers = {
    'Content-Type': 'application/json'
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    method: options.method || 'GET',
    headers: getAuthHeaders(),
    ...options
  };

  if (options.body && typeof options.body === 'object') {
    config.body = JSON.stringify(options.body);
  }

  try {
    const response = await fetch(url, config);
    const data = await response.json();

    if (!response.ok) {
      if (response.status === 401) {
        clearAuthSession();
        window.location.replace('login.html');
      }
      throw new Error(data.detail || data.message || 'API Request Failed');
    }
    return data;
  } catch (err) {
    console.error(`API Error (${endpoint}):`, err);
    throw err;
  }
}

// Global UTC Timestamp Formatter to Local Indian Standard Time (IST)
function formatTimestamp(tsStr) {
  if (!tsStr) return 'Just now';
  let str = String(tsStr).trim();
  // If naive string like "2026-09-06 05:48:56" or "2026-09-06T05:48:56", append 'Z' to parse as UTC
  if (!str.endsWith('Z') && !str.includes('+') && !str.includes('Z')) {
    str = str.replace(' ', 'T') + 'Z';
  }
  const dt = new Date(str);
  if (isNaN(dt.getTime())) return tsStr;
  return dt.toLocaleString('en-IN', {
    day: 'numeric',
    month: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  });
}
