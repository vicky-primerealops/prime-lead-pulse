// Content Script for Gmail

console.log("Prime Lead Pulse: Content script loaded.");

// Helper: inject the checkbox into the compose window toolbar
function injectToolbar(composeWindow) {
  if (composeWindow.dataset.trackerInjected) return;
  composeWindow.dataset.trackerInjected = "true";

  // Find the button row (usually contains the Send button)
  const actionRow = composeWindow.querySelector('.gU.Up');
  if (!actionRow) return;

  const trackContainer = document.createElement('div');
  trackContainer.style.display = 'inline-flex';
  trackContainer.style.alignItems = 'center';
  trackContainer.style.marginLeft = '10px';
  trackContainer.style.marginRight = '10px';
  trackContainer.style.fontSize = '13px';
  trackContainer.style.color = '#444';

  const checkbox = document.createElement('input');
  checkbox.type = 'checkbox';
  checkbox.id = 'prime-track-checkbox-' + Date.now();
  checkbox.checked = true; // default on
  checkbox.className = 'prime-track-checkbox';

  const label = document.createElement('label');
  label.htmlFor = checkbox.id;
  label.innerText = ' Track Opens & Clicks';
  label.style.marginLeft = '4px';

  trackContainer.appendChild(checkbox);
  trackContainer.appendChild(label);

  actionRow.insertBefore(trackContainer, actionRow.children[1] || null);
}

// Observe DOM for new compose windows
const observer = new MutationObserver((mutations) => {
  for (const mutation of mutations) {
    for (const node of mutation.addedNodes) {
      if (node.nodeType === Node.ELEMENT_NODE) {
        // Compose windows usually have role="dialog"
        if (node.getAttribute('role') === 'dialog' || node.querySelector('div[role="dialog"]')) {
          const composeWindows = document.querySelectorAll('div[role="dialog"]');
          composeWindows.forEach(injectToolbar);
        }
      }
    }
  }
});
observer.observe(document.body, { childList: true, subtree: true });

// Intercept Send Button clicks (Capture phase)
document.addEventListener('click', async (e) => {
  const target = e.target;
  
  // Is this the send button? (Gmail send buttons have specific classes, or aria-label="Send")
  const isSendButton = target.closest('div[aria-label^="Send"]') || 
                       (target.closest('.T-I.J-J5-Ji.aoO.v7.T-I-atl.L3') !== null);
                       
  if (!isSendButton) return;

  const composeWindow = target.closest('div[role="dialog"]');
  if (!composeWindow) return;

  const checkbox = composeWindow.querySelector('.prime-track-checkbox');
  if (!checkbox || !checkbox.checked) return;

  // We are tracking this email!
  // 1. Get sender email
  const fromField = composeWindow.querySelector('input[name="from"]');
  let senderEmail = fromField ? fromField.value : '';
  if (!senderEmail) {
    // fallback to global profile email if possible, or extract from DOM
    senderEmail = document.title.match(/([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+)/gi)?.[0] || 'unknown';
  }

  // 2. Get recipient
  const toFields = composeWindow.querySelectorAll('input[name="to"]');
  let recipient = Array.from(toFields).map(input => input.value).join(', ');
  if (!recipient) {
    // Sometimes it's in a div with email attribute
    const emailChips = composeWindow.querySelectorAll('div[email]');
    recipient = Array.from(emailChips).map(chip => chip.getAttribute('email')).join(', ');
  }

  // 3. Get subject
  const subjectField = composeWindow.querySelector('input[name="subjectbox"]');
  const subject = subjectField ? subjectField.value : 'No Subject';

  // We need to pause the send, but stopping propagation in Gmail is risky and often breaks the UI.
  // Instead, we rapidly call our background script to register the email, get the ID, and mutate the DOM before the network request fires.
  // Actually, capturing a synchronous DOM change is fine. Making an async call before letting click propagate requires `e.stopPropagation()`.
  
  e.preventDefault();
  e.stopPropagation();
  
  const originalButton = target.closest('[role="button"]');
  originalButton.style.opacity = '0.5';
  originalButton.style.pointerEvents = 'none';

  try {
    // Ask background to create email in Supabase
    chrome.runtime.sendMessage({
      action: 'CREATE_EMAIL',
      payload: { sender_email: senderEmail, recipient, subject }
    }, (response) => {
      if (response && response.success) {
        const emailRecord = response.data.email;
        
        // Get the actual message body element
        const messageBody = composeWindow.querySelector('div[aria-label="Message Body"]');
        if (messageBody) {
          // Get the base API URL from storage to construct links
          chrome.storage.local.get(['apiUrl'], (result) => {
            const apiUrl = result.apiUrl || 'http://localhost:3000';
            
            // Append Pixel
            const pixel = document.createElement('img');
            pixel.src = `${apiUrl}/api/track/pixel/${emailRecord.id}`;
            pixel.width = 1;
            pixel.height = 1;
            pixel.style.display = 'none';
            messageBody.appendChild(pixel);

            // Rewrite Links
            const links = messageBody.querySelectorAll('a');
            links.forEach(link => {
              const originalUrl = link.href;
              // Don't rewrite mailto links
              if (!originalUrl.startsWith('mailto:')) {
                link.href = `${apiUrl}/api/track/link/${emailRecord.id}?url=${encodeURIComponent(originalUrl)}`;
              }
            });

            // Now artificially trigger the send again, but bypass our interceptor
            checkbox.checked = false; // Prevent infinite loop
            originalButton.style.opacity = '1';
            originalButton.style.pointerEvents = 'auto';
            originalButton.click();
          });
        }
      } else {
        alert("Failed to track email. Ensure you are logged into Prime Lead Pulse.");
        originalButton.style.opacity = '1';
        originalButton.style.pointerEvents = 'auto';
      }
    });
  } catch (err) {
    console.error(err);
    originalButton.style.opacity = '1';
    originalButton.style.pointerEvents = 'auto';
  }
}, true); // Use capture phase!
