// ============================================================
// Prime Lead Pulse — Background Service Worker (v3)
// Fixes:
//  - Mutex lock on pollForNotifications prevents race-condition notification spam
//  - Reduced alarm frequency
//  - Smarter notification deduplication
// ============================================================

let isPolling = false; // Mutex lock to prevent concurrent polls

let refreshTokenPromise = null;

// Helper to fetch with automatic token refresh
async function fetchWithAuth(url, options, session, apiUrl) {
  let res = await fetch(url, options);
  
  if (res.status === 401 && session.refresh_token) {
    if (!refreshTokenPromise) {
      refreshTokenPromise = (async () => {
        try {
          const base = apiUrl.replace(/\/$/, '');
          const refreshRes = await fetch(`${base}/api/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: session.refresh_token })
          });
          
          if (refreshRes.ok) {
            const refreshData = await refreshRes.json();
            if (refreshData.success) {
              await chrome.storage.local.set({ session: refreshData.session });
              return refreshData.session;
            }
          }
          await chrome.storage.local.remove('session');
          return null;
        } finally {
          // Clear the promise after it's done so future expirations can trigger a new refresh
          refreshTokenPromise = null;
        }
      })();
    }
    
    const newSession = await refreshTokenPromise;
    
    if (newSession) {
      options.headers['Authorization'] = `Bearer ${newSession.access_token}`;
      res = await fetch(url, options);
    }
  }
  return res;
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'CREATE_EMAIL') {
    (async () => {
      try {
        const { session, apiUrl } = await chrome.storage.local.get(['session', 'apiUrl']);
        if (!session || !apiUrl) throw new Error('Not logged in');

        const base = apiUrl.replace(/\/$/, '');
        const res = await fetchWithAuth(`${base}/api/emails`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session.access_token}`
          },
          body: JSON.stringify(request.payload)
        }, session, apiUrl);

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

        const base = apiUrl.replace(/\/$/, '');
        const query = request.senderEmail ? `?sender_email=${encodeURIComponent(request.senderEmail)}` : '';
        const res = await fetchWithAuth(`${base}/api/emails${query}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${session.access_token}`
          }
        }, session, apiUrl);

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

        const base = apiUrl.replace(/\/$/, '');
        const res = await fetchWithAuth(`${base}/api/templates`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${session.access_token}`
          }
        }, session, apiUrl);

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
// Poll every 30 seconds (alarms have a minimum of ~30s in MV3)
chrome.alarms.create("pollStats", { periodInMinutes: 0.5 });

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === "pollStats") {
    pollForNotifications();
  }
});

pollForNotifications(); // Initial cache population

async function pollForNotifications() {
  // MUTEX LOCK: If another poll is already running, skip this one.
  // This prevents the race condition where two polls read the same knownEventIds
  // and both fire notifications for the same events.
  if (isPolling) return;
  isPolling = true;

  try {
    const { session, apiUrl, knownEventIds } = await chrome.storage.local.get(['session', 'apiUrl', 'knownEventIds']);
    if (!session || !apiUrl) return;

    const base = apiUrl.replace(/\/$/, '');
    const currentKnownIds = new Set(knownEventIds || []);
    const newEventsToNotify = []; // Collect all new events first, then batch-notify

    const res = await fetchWithAuth(`${base}/api/emails`, {
      headers: { 'Authorization': `Bearer ${session.access_token}` }
    }, session, apiUrl);
    
    if (!res.ok) return;
    const { emails } = await res.json();
    
    for (const email of emails) {
      if (!email.tracking_events) continue;
      for (const ev of email.tracking_events) {
        if (!currentKnownIds.has(ev.id)) {
          currentKnownIds.add(ev.id);

          // Only notify if we already had known events (prevents spam on first ever load)
          if (knownEventIds && knownEventIds.length > 0) {
            newEventsToNotify.push({ ev, email });
          }
        }
      }
    }

    // Save updated known IDs BEFORE sending notifications to prevent race
    await chrome.storage.local.set({ knownEventIds: Array.from(currentKnownIds) });

    // Now send notifications for genuinely new events
    // Group by email to avoid notification spam (e.g. 10 bot clicks on the same email)
    const grouped = {};
    for (const { ev, email } of newEventsToNotify) {
      // Prevent flood of old notifications if computer was asleep or token was expired
      const eventTime = new Date(ev.created_at).getTime();
      if (Date.now() - eventTime > 10 * 60 * 1000) continue; 

      const key = `${email.id}_${ev.event_type}`;
      if (!grouped[key]) {
        grouped[key] = { email, eventType: ev.event_type, count: 0 };
      }
      grouped[key].count++;
    }

    for (const key of Object.keys(grouped)) {
      const { email, eventType, count } = grouped[key];
      const isClick = eventType === 'click';
      const title = isClick ? 'Link Clicked' : 'Email Opened';
      const recipient = email.recipient || 'Unknown Recipient';
      const isMultiple = recipient.includes(',');
      
      let message;
      if (isMultiple) {
        message = isClick 
          ? `Someone clicked a link in your email to ${recipient} - "${email.subject}"` 
          : `Someone opened your email to ${recipient} - "${email.subject}"`;
      } else {
        message = isClick 
          ? `${recipient} clicked a link in your email - "${email.subject}"` 
          : `${recipient} opened your email - "${email.subject}"`;
      }
      if (count > 1) {
        message += ` (${count} times)`;
      }
        
      chrome.notifications.create(`${key}_${Date.now()}`, {
        type: 'basic',
        iconUrl: 'icon.gif',
        title,
        message,
        priority: 2
      });
    }

  } catch (err) {
    console.error('Polling error:', err);
  } finally {
    isPolling = false; // Always release the lock
  }
}
