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

  if (request.action === 'GET_TEMPLATES') {
    (async () => {
      try {
        const { session, apiUrl } = await chrome.storage.local.get(['session', 'apiUrl']);
        if (!session || !apiUrl) throw new Error('Not logged in');

        const res = await fetch(`${apiUrl}/api/templates`, {
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

// ------ Notification Polling ------
chrome.alarms.create("pollStats", { periodInMinutes: 0.25 }); // every 15 seconds approx (alarms might be delayed by Chrome)

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === "pollStats") {
    pollForNotifications();
  }
});

pollForNotifications(); // Initial cache population

async function pollForNotifications() {
  const { session, apiUrl, knownEventIds } = await chrome.storage.local.get(['session', 'apiUrl', 'knownEventIds']);
  if (!session || !apiUrl) return;

  const currentKnownIds = new Set(knownEventIds || []);
  let hasNewEvents = false;

  try {
    const res = await fetch(`${apiUrl}/api/emails`, {
      headers: { 'Authorization': `Bearer ${session.access_token}` }
    });
    if (!res.ok) return;
    const { emails } = await res.json();
    
    for (const email of emails) {
      if (!email.tracking_events) continue;
      for (const ev of email.tracking_events) {
        if (!currentKnownIds.has(ev.id)) {
          currentKnownIds.add(ev.id);
          hasNewEvents = true;

          // Only notify if we already had known events (prevents spam on first ever load)
          if (knownEventIds && knownEventIds.length > 0) {
            const isClick = ev.event_type === 'click';
            const title = isClick ? 'Link Clicked!' : 'Email Opened!';
            const recipient = email.recipient || 'Unknown Recipient';
            const message = isClick 
              ? `${recipient} clicked a link in "${email.subject}"` 
              : `${recipient} opened your email "${email.subject}"`;
              
            chrome.notifications.create(ev.id, {
              type: 'basic',
              iconUrl: 'icon.gif',
              title,
              message,
              priority: 2
            });
          }
        }
      }
    }

    if (hasNewEvents) {
      await chrome.storage.local.set({ knownEventIds: Array.from(currentKnownIds) });
    }
  } catch (err) {
    console.error('Polling error:', err);
  }
}
