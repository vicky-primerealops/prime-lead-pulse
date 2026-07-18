import argparse
import base64
import email.policy
import imaplib
import os
import smtplib
import time
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient.discovery import build
import config as cfg

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
log = logging.getLogger(__name__)

# ── How many emails to send per run ────────────────────────────────────────
EMAILS_PER_RUN = 30

# ── Tracking pixel (set to your Vercel domain) ────────────────────────────
# Once your dev team deploys the tracking API, set this to True
TRACKING_ENABLED = True
TRACKING_URL      = "https://props-platform-api.vercel.app/api/track"
TRACKING_CTX      = "prime-realops-outreach"   # campaign label for the dashboard


# ── GoDaddy IMAP settings ───────────────────────────────────────────────────
IMAP_HOST = "imap.secureserver.net"
IMAP_PORT = 993
SENT_FOLDER_CANDIDATES = ["Sent", "Sent Items", "INBOX.Sent", "[Gmail]/Sent Mail"]

# ── Email templates (live here so cloud never mangles them) ─────────────────
EMAIL_SUBJECT = "{name} X PrimeRealOps | Streamlining Your Real Estate Operations"

EMAIL_BODY_TEXT = """\
Hi {name},

Your highest value as a broker is closing deals and scaling your team, not getting bogged down by backend administration and paperwork.

At Prime Real Ops, we function as your complete backend engine. We plug directly into your existing platforms to handle the heavy lifting across three core areas:

- Listing Management: Flawless MLS data entry and compliance checks with a 100% accuracy guarantee.
- Transaction Coordination: Seamless contract-to-close management to keep your clients happy and ensure on-time closings.
- Executive Services: Dedicated, elite real estate VAs to manage your inbox, CRM, and daily operational friction.

With our 72-Hour Rapid Deployment, we can take this off your plate seamlessly with minimal onboarding downtime.

If you are ready to stop managing chaos and start focusing on growth, I'd love to connect.

Are you open to a brief chat? We can set up a time here: [https://calendar.app.google/wtiXBDUQM3wcamJR9]

Best Regards,

Vicky Thakkar
Founder | PrimeRealOps
+91 88052 92130, +1(678) 678-9750
Mumbai, India

"Jack of all trades, master of none,
But oftentimes better than a master of one."
"""

EMAIL_BODY_HTML = """\
<!DOCTYPE html>
<html>
<head>
<style>
  .body-text {{ font-family: Georgia, serif; color: #333333; line-height: 1.6; font-size: 15px; }}
  .sig-text {{ font-family: Arial, Helvetica, sans-serif; color: #000000; }}
  .blue-link {{ color: #0056b3; text-decoration: none; font-weight: bold; }}
</style>
</head>
<body style="margin: 0; padding: 0;">

  <div class="body-text">
    <p style="margin-bottom: 20px;"><strong>Hi {name},</strong></p>

    <p style="margin-bottom: 20px;">Your highest value as a broker is closing deals and scaling your team, not getting bogged down by backend administration and paperwork.</p>

    <p style="margin-bottom: 20px;">At <a href="https://primerealops.com" class="blue-link">Prime Real Ops</a>, we function as your complete backend engine. We plug directly into your existing platforms to handle the heavy lifting across three core areas:</p>

    <ul style="margin-bottom: 20px; padding-left: 20px;">
      <li style="margin-bottom: 10px;"><strong>Listing Management:</strong> Flawless MLS data entry and compliance checks with a 100% accuracy guarantee.</li>
      <li style="margin-bottom: 10px;"><strong>Transaction Coordination:</strong> Seamless contract-to-close management to keep your clients happy and ensure on-time closings.</li>
      <li style="margin-bottom: 10px;"><strong>Executive Services:</strong> Dedicated, elite real estate VAs to manage your inbox, CRM, and daily operational friction.</li>
    </ul>

    <p style="margin-bottom: 20px;">With our 72-Hour Rapid Deployment, we can take this off your plate seamlessly with minimal onboarding downtime.</p>

    <p style="margin-bottom: 20px;">If you are ready to stop managing chaos and start focusing on growth, I'd love to connect.</p>

    <p style="margin-bottom: 30px;"><strong>Are you open to a brief chat? We can set up a time <a href="https://calendar.app.google/wtiXBDUQM3wcamJR9" class="blue-link">[HERE]</a>.</strong></p>

    <p style="margin-bottom: 25px;">Best Regards,</p>
  </div>

  <table cellpadding="0" cellspacing="0" border="0" style="width: 100%; max-width: 500px; font-family: Arial, Helvetica, sans-serif;">
    <tr>
      <td width="110" style="vertical-align: top; text-align: center; padding-right: 15px;">
        <img src="https://lh3.googleusercontent.com/d/1Zz6uT1DvadvwclNj0Vihrj0N42gKT9cE" alt="Vicky Thakkar" width="90" height="90" style="border-radius: 50%; display: block; margin: 0 auto 10px auto; object-fit: cover;">
        <a href="https://calendar.app.google/wtiXBDUQM3wcamJR9" style="font-weight: bold; color: #0056b3; text-decoration: underline; font-size: 13px;">Book A Call</a>
      </td>
      <td width="3" style="background-color: #0056b3; vertical-align: top;">&nbsp;</td>
      <td style="vertical-align: top; padding-left: 15px;">
        <p style="margin: 0 0 2px 0; font-size: 17px; font-weight: bold; color: #000000; font-family: Georgia, serif;">Vicky Thakkar</p>
        <p style="margin: 0 0 10px 0; font-size: 13px; color: #000000;"><strong>Founder | PrimeRealOps</strong></p>
        <p style="margin: 0 0 4px 0; font-size: 12px; color: #333333;">&#128222; +91 88052 92130, +1(678) 678-9750</p>
        <p style="margin: 0 0 10px 0; font-size: 12px; color: #333333;">&#128205; Mumbai, India</p>
        <p style="margin: 0 0 10px 0;">
          <a href="https://instagram.com/v.p.thakkar" style="text-decoration: none; margin-right: 6px;"><img src="https://cdn-icons-png.flaticon.com/512/174/174855.png" width="18" height="18" alt="Instagram"></a>
          <a href="https://www.linkedin.com/in/vickythegeneralist/" style="text-decoration: none; margin-right: 6px;"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="18" height="18" alt="LinkedIn"></a>
          <a href="https://wa.me/16786789750" style="text-decoration: none;"><img src="https://cdn-icons-png.flaticon.com/512/733/733585.png" width="18" height="18" alt="WhatsApp"></a>
        </p>
        <p style="margin: 0; font-size: 12px; font-weight: bold; line-height: 1.6; font-family: Georgia, serif; color: #333333;">
          "Jack of all trades, master of none,<br>But oftentimes better than a master of one."
        </p>
      </td>
    </tr>
  </table>

</body>
</html>
"""


def get_imap_sent_folder(imap_conn):
    _, folder_list = imap_conn.list()
    available = []
    for entry in folder_list:
        decoded = entry.decode() if isinstance(entry, bytes) else entry
        available.append(decoded)
    for candidate in SENT_FOLDER_CANDIDATES:
        for folder_entry in available:
            if f'"{candidate}"' in folder_entry or f' {candidate}' in folder_entry:
                return candidate
    log.warning("Could not detect Sent folder; defaulting to 'Sent'.")
    return "Sent"


def save_to_sent(msg_bytes):
    try:
        with imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT) as imap:
            imap.login(cfg.SMTP_USER, cfg.SMTP_PASSWORD)
            sent_folder = get_imap_sent_folder(imap)
            imap.append(
                sent_folder,
                "\\Seen",
                imaplib.Time2Internaldate(time.time()),
                msg_bytes,
            )
            log.debug("  ↳ Saved to IMAP Sent folder: %s", sent_folder)
    except Exception as e:
        log.warning("  ↳ Could not save to Sent folder: %s", e)


def get_contacts_from_sheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = service_account.Credentials.from_service_account_file(
        cfg.SERVICE_ACCOUNT_FILE, scopes=scopes
    )
    service = build("sheets", "v4", credentials=creds)
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=cfg.SPREADSHEET_ID, range="Sheet1!A2:C")
        .execute()
    )
    rows = result.get("values", [])
    contacts = []
    for i, row in enumerate(rows, start=2):
        if len(row) < 2:
            continue
        name = row[0].strip()
        email = row[1].strip()
        sent_status = row[2].strip() if len(row) >= 3 else ""
        if sent_status:
            log.debug("Skipping (already sent) → %s <%s>", name, email)
            continue
        if name and email:
            contacts.append({"name": name, "email": email, "row": i})
    return contacts, service


def mark_as_sent(service, row):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    service.spreadsheets().values().update(
        spreadsheetId=cfg.SPREADSHEET_ID,
        range=f"Sheet1!C{row}",
        valueInputOption="RAW",
        body={"values": [[timestamp]]},
    ).execute()


def build_message(to_name, to_email):
    first_name = to_name.split()[0]
    subject   = EMAIL_SUBJECT.format(name=first_name)
    body_text = EMAIL_BODY_TEXT.format(name=first_name)
    body_html = EMAIL_BODY_HTML.format(name=first_name)

    # Inject tracking pixel if enabled
    if TRACKING_ENABLED:
        encoded_email = base64.b64encode(to_email.encode()).decode()  # standard base64
        pixel_tag = (
            f'<img src="{TRACKING_URL}?id={encoded_email}&ctx={TRACKING_CTX}" '
            f'width="1" height="1" alt="" style="display:none" />'
        )
        body_html = body_html.replace("</body>", f"{pixel_tag}\n</body>")

    # ── Build final message ──────────────────────────────────────────
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{cfg.FROM_NAME} <{cfg.SMTP_USER}>"
    msg["To"]      = to_email
    msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(body_html, "html"))
    return msg


def send_emails(contacts, service):
    batch = contacts[:EMAILS_PER_RUN]
    sent_count = 0
    for contact in batch:
        try:
            msg = build_message(contact["name"], contact["email"])
            raw_msg = msg.as_bytes(policy=email.policy.SMTP)

            with smtplib.SMTP_SSL(cfg.SMTP_HOST, cfg.SMTP_PORT) as server:
                server.login(cfg.SMTP_USER, cfg.SMTP_PASSWORD)
                server.send_message(msg)

            save_to_sent(raw_msg)
            mark_as_sent(service, contact["row"])

            sent_count += 1
            log.info(
                "✓ Sent (%d/%d) → %s <%s>",
                sent_count, len(batch), contact["name"], contact["email"],
            )
            time.sleep(cfg.SEND_DELAY_SECONDS)
        except Exception as e:
            log.error("✗ Failed → %s <%s>: %s", contact["name"], contact["email"], e)

    log.info("─── Done. %d email(s) sent this run. ───", sent_count)


def main():
    parser = argparse.ArgumentParser(description="Send outreach emails from Google Sheet.")
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Skip confirmation prompt (used by automated schedulers).",
    )
    args = parser.parse_args()

    log.info("Fetching unsent contacts from Google Sheet…")
    contacts, service = get_contacts_from_sheet()

    if not contacts:
        log.info("No unsent contacts found. Nothing to do.")
        return

    batch_size = min(len(contacts), EMAILS_PER_RUN)

    if args.auto:
        log.info("Auto mode: sending to the next %d unsent contact(s)…", batch_size)
        send_emails(contacts, service)
    else:
        answer = input(
            f"\nFound {len(contacts)} unsent contact(s). "
            f"Ready to send to the next {batch_size}. Proceed? [y/N]: "
        )
        if answer.strip().lower() == "y":
            send_emails(contacts, service)
        else:
            log.info("Aborted by user.")


if __name__ == "__main__":
    main()