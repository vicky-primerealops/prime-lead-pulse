// This script runs on the Prime Lead Pulse dashboard to automatically sync authentication to the extension
function syncAuth() {
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key && key.startsWith('sb-') && key.endsWith('-auth-token')) {
      const tokenStr = localStorage.getItem(key);
      try {
        const tokenObj = JSON.parse(tokenStr);
        if (tokenObj && tokenObj.access_token) {
          chrome.runtime.sendMessage({
            action: 'DASHBOARD_LOGIN',
            session: tokenObj,
            apiUrl: window.location.origin
          });
        }
      } catch(e) {}
    }
  }
}

// Sync on load
setTimeout(syncAuth, 1000); // Wait for React to potentially write it

// Monitor for logins/logouts
window.addEventListener('storage', (e) => {
  if (e.key && e.key.startsWith('sb-') && e.key.endsWith('-auth-token')) {
    if (!e.newValue) {
      chrome.runtime.sendMessage({ action: 'DASHBOARD_LOGOUT' });
    } else {
      syncAuth();
    }
  }
});
