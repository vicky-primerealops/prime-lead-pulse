// Helper to get the correct session for a specific Gmail sender
async function getSessionForSender(senderEmail) {
  const { session, sessions } = await chrome.storage.local.get(['session', 'sessions']);
  
  // 1. Try to find an exact match in the multi-tenant sessions map
  if (sessions && sessions[senderEmail]) {
    return sessions[senderEmail];
  }
  
  // 2. Fallback: check if the legacy single session matches the sender
  if (session && session.user && session.user.email === senderEmail) {
    return session;
  }
  
  // 3. Strict separation: if we don't have a session specifically for this email, we cannot track it.
  throw new Error('Account mismatch! You are sending from ' + senderEmail + ' but you are not logged into a matching Prime Lead Pulse account. Please log into the dashboard with ' + senderEmail + ' to link this account.');
}
