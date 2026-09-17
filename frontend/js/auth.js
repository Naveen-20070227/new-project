/* Authentication Module (Mobile + OTP) */

let currentAuthMode = 'register'; // 'register' or 'login'
let otpCooldownInterval = null;

function switchAuthTab(mode) {
  currentAuthMode = mode;
  document.querySelectorAll('.auth-tab-btn').forEach(btn => btn.classList.remove('active'));
  document.getElementById(`tab-${mode}`).classList.add('active');

  const regNameGroup = document.getElementById('group-beneficiary-name');
  if (mode === 'register') {
    regNameGroup.style.display = 'block';
    document.getElementById('auth-submit-btn').innerText = 'Request OTP & Register';
  } else {
    regNameGroup.style.display = 'none';
    document.getElementById('auth-submit-btn').innerText = 'Request OTP & Login';
  }

  // Reset OTP view state
  resetOtpStep();
}

function resetOtpStep() {
  document.getElementById('otp-step-container').style.display = 'none';
  document.getElementById('request-otp-step').style.display = 'block';
  document.getElementById('dev-otp-display').style.display = 'none';
  document.getElementById('auth-error-alert').style.display = 'none';
}

async function handleRequestOtp() {
  const mobileInput = document.getElementById('auth-mobile').value.trim();
  const nameInput = document.getElementById('auth-name').value.trim();
  const alertBox = document.getElementById('auth-error-alert');

  alertBox.style.display = 'none';

  if (!mobileInput || mobileInput.length < 10) {
    alertBox.innerText = 'Please enter a valid 10-digit mobile number.';
    alertBox.style.display = 'flex';
    return;
  }

  if (currentAuthMode === 'register' && (!nameInput || nameInput.length < 2)) {
    alertBox.innerText = 'Please enter your full Beneficiary Name.';
    alertBox.style.display = 'flex';
    return;
  }

  const submitBtn = document.getElementById('auth-submit-btn');
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="spinner"></span> Requesting OTP...';

  try {
    const res = await apiRequest('/auth/request-otp', {
      method: 'POST',
      body: { mobile_number: mobileInput }
    });

    // Show OTP input view
    document.getElementById('request-otp-step').style.display = 'none';
    document.getElementById('otp-step-container').style.display = 'block';

    // Show Dev OTP Box if returned
    if (res.dev_otp) {
      const devBox = document.getElementById('dev-otp-display');
      document.getElementById('dev-otp-code').innerText = res.dev_otp;
      devBox.style.display = 'flex';
    }

    startCooldownTimer(res.cooldown_seconds || 60);

  } catch (err) {
    alertBox.innerText = err.message || 'Failed to send OTP.';
    alertBox.style.display = 'flex';
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerText = currentAuthMode === 'register' ? 'Request OTP & Register' : 'Request OTP & Login';
  }
}

function startCooldownTimer(seconds) {
  let remaining = seconds;
  const timerElem = document.getElementById('resend-timer-text');
  const resendBtn = document.getElementById('resend-otp-btn');
  
  if (resendBtn) resendBtn.disabled = true;

  if (otpCooldownInterval) clearInterval(otpCooldownInterval);

  otpCooldownInterval = setInterval(() => {
    remaining--;
    if (timerElem) timerElem.innerText = `Resend available in ${remaining}s`;
    if (remaining <= 0) {
      clearInterval(otpCooldownInterval);
      if (timerElem) timerElem.innerText = '';
      if (resendBtn) resendBtn.disabled = false;
    }
  }, 1000);
}

async function handleVerifyAndSubmit() {
  const mobileInput = document.getElementById('auth-mobile').value.trim();
  const nameInput = document.getElementById('auth-name').value.trim();
  const otpInput = document.getElementById('auth-otp').value.trim();
  const alertBox = document.getElementById('auth-error-alert');

  alertBox.style.display = 'none';

  if (!otpInput || otpInput.length < 4) {
    alertBox.innerText = 'Please enter the OTP received.';
    alertBox.style.display = 'flex';
    return;
  }

  const verifyBtn = document.getElementById('verify-otp-btn');
  verifyBtn.disabled = true;
  verifyBtn.innerHTML = '<span class="spinner"></span> Verifying...';

  try {
    let endpoint = currentAuthMode === 'register' ? '/auth/register' : '/auth/login';
    let bodyData = {
      mobile_number: mobileInput,
      otp: otpInput
    };
    if (currentAuthMode === 'register') {
      bodyData.beneficiary_name = nameInput;
    }

    const tokenRes = await apiRequest(endpoint, {
      method: 'POST',
      body: bodyData
    });

    // Store Session (SessionStorage - lost on refresh)
    setAuthToken(tokenRes.access_token, {
      user_id: tokenRes.user_id,
      name: tokenRes.beneficiary_name,
      mobile: tokenRes.mobile_number,
      profile_complete: tokenRes.profile_complete
    });

    // Mark as fresh login transition
    sessionStorage.setItem('yojana_fresh_login', 'true');

    // Redirect to Dashboard
    window.location.href = 'dashboard.html';

  } catch (err) {
    alertBox.innerText = err.message || 'OTP Verification failed.';
    alertBox.style.display = 'flex';
  } finally {
    verifyBtn.disabled = false;
    verifyBtn.innerText = 'Verify OTP & Proceed';
  }
}

// Auto-switch Auth tab mode based on URL parameter (?mode=login or ?mode=register)
document.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  const modeParam = urlParams.get('mode');
  if (modeParam === 'login' || modeParam === 'register') {
    switchAuthTab(modeParam);
  }
});

