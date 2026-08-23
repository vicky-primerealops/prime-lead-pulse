chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'CREATE_EMAIL') {
    (async () => {
      try {
        const { session, apiUrl } = await chrome.storage.local.get(['session', 'apiUrl']);
        if (!session || !apiUrl) throw new Error('Not logged in');

        const res = await fetch(`${apiUrl}/api/emails`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session.access_token}`
          },
          body: JSON.stringify(request.payload)
        });

        const data = await res.json();
        sendResponse({ success: res.ok, data });
      } catch (err) {
        sendResponse({ success: false, error: err.message });
      }
    })();
    return true; // Keep message channel open for async response
  }

  if (request.action === 'GET_STATS') {
    (async () => {
      try {
        const { session, apiUrl } = await chrome.storage.local.get(['session', 'apiUrl']);
        if (!session || !apiUrl) throw new Error('Not logged in');

        const query = request.senderEmail ? `?sender_email=${encodeURIComponent(request.senderEmail)}` : '';
        const res = await fetch(`${apiUrl}/api/emails${query}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${session.access_token}`
          }
        });

        const data = await res.json();
        sendResponse({ success: res.ok, data });
      } catch (err) {
        sendResponse({ success: false, error: err.message });
      }
    })();
    return true;
  }
});
