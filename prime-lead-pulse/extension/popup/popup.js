document.addEventListener('DOMContentLoaded', async () => {
  const loginSection = document.getElementById('loginSection');
  const loggedInSection = document.getElementById('loggedInSection');
  const errorMsg = document.getElementById('errorMsg');
  
  const apiUrlInput = document.getElementById('apiUrl');
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('password');
  
  const loginBtn = document.getElementById('loginBtn');
  const logoutBtn = document.getElementById('logoutBtn');

  // Check if already logged in
  const result = await chrome.storage.local.get(['session', 'apiUrl']);
  if (result.session && result.apiUrl) {
    showLoggedIn();
  }

  loginBtn.addEventListener('click', async () => {
    const apiUrl = apiUrlInput.value.trim().replace(/\/$/, "");
    const email = emailInput.value.trim();
    const password = passwordInput.value;

    if (!apiUrl || !email || !password) {
      errorMsg.textContent = 'Please fill all fields.';
      return;
    }

    loginBtn.disabled = true;
    loginBtn.textContent = 'Logging in...';
    errorMsg.textContent = '';

    try {
      const res = await fetch(`${apiUrl}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      let data;
      const text = await res.text();
      try {
        data = JSON.parse(text);
      } catch (e) {
        throw new Error(`Server returned non-JSON. Status: ${res.status}. Body: ${text.substring(0, 50)}`);
      }

      if (res.ok && data.success) {
        await chrome.storage.local.set({
          session: data.session,
          apiUrl: apiUrl
        });
        showLoggedIn();
      } else {
        errorMsg.textContent = data.error || `Login failed (Status: ${res.status})`;
      }
    } catch (err) {
      console.error(err);
      errorMsg.textContent = 'API Error: ' + err.message;
    } finally {
      loginBtn.disabled = false;
      loginBtn.textContent = 'Log In';
    }
  });

  logoutBtn.addEventListener('click', async () => {
    await chrome.storage.local.remove(['session', 'apiUrl']);
    loginSection.classList.remove('hidden');
    loggedInSection.classList.add('hidden');
  });

  function showLoggedIn() {
    loginSection.classList.add('hidden');
    loggedInSection.classList.remove('hidden');
  }
});
