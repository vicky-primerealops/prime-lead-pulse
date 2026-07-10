import argparse
import email.policy
import imaplib
import smtplib
import time
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient.discovery import build
import config as cfg  # Pulling your real config file

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
log = logging.getLogger(__name__)

# ── How many emails to send per run ────────────────────────────────────────
EMAILS_PER_RUN = 50

# ── GoDaddy IMAP settings ───────────────────────────────────────────────────
IMAP_HOST = "imap.secureserver.net"
IMAP_PORT = 993

# GoDaddy Sent folder name (try "Sent" first; fallback handled automatically)
SENT_FOLDER_CANDIDATES = ["Sent", "Sent Items", "INBOX.Sent", "[Gmail]/Sent Mail"]


def get_imap_sent_folder(imap_conn):
    """
    Lists available IMAP folders and returns the name of the Sent folder.
    Falls back to the first candidate that exists, or 'Sent' if none found.
    """
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
    """
    Connects to GoDaddy IMAP and appends the raw email bytes
    to the Sent folder so it shows up in your GoDaddy webmail Sent box.
    """
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
    """
    Reads the sheet and returns only contacts that have NOT been sent yet.
    Reads columns A (Name), B (Email), C (Sent timestamp).
    Skips any row where column C already has a value.
    """
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = service_account.Credentials.from_service_account_file(
        cfg.SERVICE_ACCOUNT_FILE, scopes=scopes
    )
    service = build("sheets", "v4", credentials=creds)

    result = (
        service.spreadsheets()
        .values()
        .get(
            spreadsheetId=cfg.SPREADSHEET_ID,
            range="Sheet1!A2:C",
        )
        .execute()
    )
    rows = result.get("values", [])

    contacts = []
    for i, row in enumerate(rows, start=2):
        if len(row) < 2:
            continue

        name = row[0].strip()
        email = row[1].strip()

        # Column C — if it has any value, email was already sent → skip
        sent_status = row[2].strip() if len(row) >= 3 else ""
        if sent_status:
            log.debug("Skipping (already sent) → %s <%s>", name, email)
            continue

        if name and email:
            contacts.append({"name": name, "email": email, "row": i})

    return contacts, service


def mark_as_sent(service, row):
    """Writes the current date & time into column C for the given row."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    service.spreadsheets().values().update(
        spreadsheetId=cfg.SPREADSHEET_ID,
        range=f"Sheet1!C{row}",
        valueInputOption="RAW",
        body={"values": [[timestamp]]},
    ).execute()


def build_message(to_name, to_email):
    first_name = to_name.split()[0]
    subject = cfg.EMAIL_SUBJECT.format(name=first_name)
    body_text = cfg.EMAIL_BODY_TEXT.format(name=first_name)
    body_html = cfg.EMAIL_BODY_HTML.format(name=first_name)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{cfg.FROM_NAME} <{cfg.SMTP_USER}>"
    msg["To"] = to_email
    msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(body_html, "html"))
    return msg


def send_emails(contacts, service):
    """
    Sends emails to the first EMAILS_PER_RUN unsent contacts.
    After each send:
      - Saves a copy to GoDaddy Sent folder via IMAP.
      - Marks the row in the sheet with a timestamp.
    """
    batch = contacts[:EMAILS_PER_RUN]
    sent_count = 0

    for contact in batch:
        try:
            msg = build_message(contact["name"], contact["email"])

            # Generate bytes with proper CRLF (\r\n) line endings — required by
            # RFC 822 / 822.bis. email.policy.SMTP handles this automatically.
            raw_msg = msg.as_bytes(policy=email.policy.SMTP)

            # 1️⃣  Send via SMTP
            with smtplib.SMTP_SSL(cfg.SMTP_HOST, cfg.SMTP_PORT) as server:
                server.login(cfg.SMTP_USER, cfg.SMTP_PASSWORD)
                server.send_message(msg)

            # 2️⃣  Save copy to GoDaddy Sent folder via IMAP
            save_to_sent(raw_msg)

            # 3️⃣  Stamp the sheet row with sent timestamp
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
        help="Skip the confirmation prompt (used by automated schedulers like GitHub Actions).",
    )
    args = parser.parse_args()

    log.info("Fetching unsent contacts from Google Sheet…")
    contacts, service = get_contacts_from_sheet()

    if not contacts:
        log.info("No unsent contacts found. Nothing to do.")
        return

    batch_size = min(len(contacts), EMAILS_PER_RUN)

    if args.auto:
        # Running in automated/cloud mode — no human to prompt
        log.info("Auto mode: sending to the next %d unsent contact(s)…", batch_size)
        send_emails(contacts, service)
    else:
        # Running locally — ask for confirmation
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