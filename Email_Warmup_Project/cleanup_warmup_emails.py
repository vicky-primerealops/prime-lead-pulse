"""
cleanup_warmup_emails.py
────────────────────────
SAFELY deletes ONLY warmup emails.

Safety rule (STRICT):
  An email is deleted ONLY if:
    • FROM is one of your warmup accounts
    AND
    • TO is one of your warmup accounts

  If either side is an outside address, the email is NEVER touched.

Run locally:
  python cleanup_warmup_emails.py
"""

import csv
import email as emaillib
import imaplib
import logging
import time
import random

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Folders to clean ──────────────────────────────────────────────────────────
FOLDERS_TO_CHECK = [
    "INBOX",
    "Sent",
    "Sent Items",
    "[Gmail]/Sent Mail",
    "[Gmail]/Spam",
    "[Gmail]/Trash",
    "Spam",
    "Junk",
    "Trash",
    "INBOX.Sent",
    "INBOX.Trash",
    "INBOX.Junk",
]


def get_imap_host(email_addr):
    email_lower = email_addr.lower()
    if "@gmail.com" in email_lower or "@diyflatfee.com" in email_lower:
        return "imap.gmail.com"
    return "imap.secureserver.net"


def load_accounts(filename="warmup_accounts.csv"):
    accounts = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                e = row.get("Email", "").strip().lower()
                p = row.get("AppPassword", "").strip()
                if e and p:
                    accounts.append({"email": e, "password": p})
    except Exception as exc:
        log.error(f"Could not load {filename}: {exc}")
    return accounts


def list_all_folders(mail):
    status, folder_list = mail.list()
    folders = []
    if status != "OK":
        return folders
    for entry in folder_list:
        decoded = entry.decode() if isinstance(entry, bytes) else entry
        parts = decoded.split('"/"')
        if len(parts) >= 2:
            name = parts[-1].strip().strip('"')
        else:
            name = decoded.split()[-1].strip().strip('"')
        folders.append(name)
    return folders


def extract_addresses(header_value):
    """Extract all email addresses from a header value like 'Name <email@example.com>'."""
    if not header_value:
        return []
    addrs = []
    for part in header_value.split(","):
        part = part.strip()
        if "<" in part and ">" in part:
            addr = part[part.index("<") + 1:part.index(">")].strip().lower()
        else:
            addr = part.strip().lower()
        if "@" in addr:
            addrs.append(addr)
    return addrs


def delete_warmup_emails_in_folder(mail, folder, warmup_set):
    """
    For every email in this folder that was sent FROM a warmup address,
    fetch its headers and check if ALL recipients (TO/CC) are also warmup addresses.
    Only then delete it.
    """
    try:
        status, _ = mail.select(folder, readonly=False)
        if status != "OK":
            return 0
    except Exception:
        return 0

    deleted = 0

    # Search for emails FROM any of the warmup addresses
    for addr in warmup_set:
        try:
            status, messages = mail.search(None, f'FROM "{addr}"')
            if status != "OK" or not messages[0]:
                continue
            nums = messages[0].split()
            if not nums:
                continue

            for num in nums:
                try:
                    # Fetch only the headers to check TO/CC
                    typ, data = mail.fetch(num, "(BODY[HEADER.FIELDS (FROM TO CC)])")
                    if typ != "OK" or not data or not data[0]:
                        continue

                    raw_headers = data[0][1]
                    msg = emaillib.message_from_bytes(raw_headers)

                    from_addrs = extract_addresses(msg.get("From", ""))
                    to_addrs   = extract_addresses(msg.get("To", ""))
                    cc_addrs   = extract_addresses(msg.get("Cc", ""))
                    all_recipients = to_addrs + cc_addrs

                    # ── STRICT SAFETY CHECK ───────────────────────────────
                    # From must be a warmup address
                    from_is_warmup = all(a in warmup_set for a in from_addrs) and len(from_addrs) > 0
                    # ALL recipients must also be warmup addresses
                    recipients_are_warmup = all(a in warmup_set for a in all_recipients) and len(all_recipients) > 0

                    if from_is_warmup and recipients_are_warmup:
                        mail.store(num, "+FLAGS", "\\Deleted")
                        deleted += 1
                        log.info(f"      ✓ Deleting: {from_addrs} → {all_recipients}")
                    else:
                        # At least one outsider involved — skip safely
                        log.debug(f"      ⏭ Skipping (outsider involved): {from_addrs} → {all_recipients}")

                except Exception as exc:
                    log.warning(f"      Error processing message {num}: {exc}")

        except Exception as exc:
            log.warning(f"      Search error for {addr}: {exc}")

    if deleted:
        try:
            mail.expunge()
        except Exception as exc:
            log.warning(f"      Expunge error: {exc}")

    return deleted


def clean_account(account, warmup_set):
    email_addr = account["email"]
    password   = account["password"]
    imap_host  = get_imap_host(email_addr)

    log.info(f"\n{'─'*60}")
    log.info(f"  Cleaning: {email_addr}")
    log.info(f"{'─'*60}")

    total_deleted = 0
    try:
        mail = imaplib.IMAP4_SSL(imap_host)
        mail.login(email_addr, password)

        existing_folders = list_all_folders(mail)
        folders_to_clean = [f for f in FOLDERS_TO_CHECK if f in existing_folders]
        if not folders_to_clean:
            folders_to_clean = ["INBOX"]

        for folder in folders_to_clean:
            log.info(f"  Checking folder: {folder}")
            count = delete_warmup_emails_in_folder(mail, folder, warmup_set)
            total_deleted += count
            if count:
                log.info(f"    ✓ Deleted {count} warmup emails from '{folder}'")
            else:
                log.info(f"    ✓ '{folder}' is clean.")

        mail.close()
        mail.logout()

    except imaplib.IMAP4.error as exc:
        log.error(f"  IMAP login failed for {email_addr}: {exc}")
    except Exception as exc:
        log.error(f"  Unexpected error for {email_addr}: {exc}")

    log.info(f"  Total deleted from {email_addr}: {total_deleted}")
    return total_deleted


def main():
    log.info("=" * 60)
    log.info("  WARMUP EMAIL CLEANER (STRICT MODE)")
    log.info("  Deletes ONLY emails where FROM and TO")
    log.info("  are BOTH within your warmup accounts.")
    log.info("  Real emails are completely safe.")
    log.info("=" * 60)

    accounts = load_accounts()
    if not accounts:
        log.error("No accounts loaded from warmup_accounts.csv. Aborting.")
        return

    # Build a set of all warmup addresses for fast lookups
    warmup_set = set(acc["email"] for acc in accounts)
    log.info(f"Loaded {len(accounts)} accounts.")
    log.info(f"Warmup address pool: {warmup_set}\n")

    grand_total = 0
    for i, account in enumerate(accounts, 1):
        log.info(f"\n[Account {i}/{len(accounts)}]")
        deleted = clean_account(account, warmup_set)
        grand_total += deleted
        if i < len(accounts):
            delay = random.randint(15, 30)
            log.info(f"Sleeping for {delay} seconds before next account to prevent login limits...")
            time.sleep(delay)

    log.info("\n" + "=" * 60)
    log.info(f"  CLEANUP COMPLETE. Total warmup emails deleted: {grand_total}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
