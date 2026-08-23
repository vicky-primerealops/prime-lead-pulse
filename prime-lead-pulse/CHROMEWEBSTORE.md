# Chrome Web Store Listing: Prime Lead Pulse

## Store Listing Metadata

**Name:** Prime Lead Pulse  
**Short Name:** Prime Lead Pulse  
**Summary:** Track email opens and link clicks directly inside Gmail. Seamless, secure, and self-hosted.  
**Description:**  
Prime Lead Pulse is an essential tool for professionals who need to know when their emails are opened and when their links are clicked. Built with privacy in mind, it integrates seamlessly into the Gmail compose window. 

Features:
- Track if an email was opened using invisible 1x1 pixels.
- Track link clicks inside your emails.
- Beautiful, non-intrusive UI built directly into the Gmail Compose window.
- Fully supports multiple Gmail accounts.
- Bring Your Own Backend (BYOB): Connect to your own private Supabase & Next.js backend to ensure 100% data ownership.

**Category:** Productivity  

## Permissions Justification

The extension requests the following permissions. None of these are used to collect data for third-party servers. All data is routed directly to the user's privately configured API.

- **`storage`**: Required to securely store the user's API URL and authentication session token locally on the device, allowing them to remain logged in.
- **`scripting`**: Required to inject the tracking functionality and UI elements directly into the `mail.google.com` interface.

## Host Permissions Justification

- **`*://mail.google.com/*`**: Required to inject the "Track this Email" checkbox into the compose window and intercept the send action to append the tracking pixel.
- **`*://*.supabase.co/*`**: Required to authenticate the user securely against their personal Supabase backend project.
- **`*://localhost/*`**: Required during local development and testing to connect to the local Next.js API instance.

## Privacy Policy

**Data Collection and Storage:**
Prime Lead Pulse does NOT collect, store, or transmit your data to any centralized developer server. It acts purely as a local client that connects directly to your own self-hosted backend. The developer of this extension has zero access to your emails, tracking logs, or authentication tokens.

**Permissions Usage:**
The extension only reads the DOM of `mail.google.com` during the "Compose" and "Send" phases to determine the recipient and subject for tracking purposes. This data is transmitted immediately and exclusively to the API URL that the user configures in the extension's login popup.

**Third Parties:**
No data is sold or shared with any third parties.

## Pre-Publish Checklist
- [ ] Create 128x128 icon and place in `extension/icons/icon-128.png`.
- [ ] Take a 1280x800 screenshot of the extension working in Gmail.
- [ ] Zip the `extension` directory (excluding `CHROMEWEBSTORE.md` and the rest of the Next.js project).
- [ ] Upload to the Chrome Developer Dashboard.
