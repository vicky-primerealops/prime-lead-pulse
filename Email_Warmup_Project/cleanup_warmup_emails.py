"""
cleanup_warmup_emails.py
────────────────────────
Deletes all warmup emails from every account in warmup_accounts.csv.

What it deletes:
  • Any email FROM one of your own warmup accounts (sent to another)
  • Any email TO one of your own warmup accounts (received from another)
  • Checks: INBOX, Sent, [Gmail]/Sent Mail, Spam, Junk, Trash

Run locally:
  python cleanup_warmup_emails.py

Run on GitHub Actions:
  Trigger the "Cleanup Warmup Emails" workflow manually.
"""

import csv
import imaplib
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Folders to clean in each account ─────────────────────────────────────────
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
                e = row.get("Email", "").strip()
                p = row.get("AppPassword", "").strip()
                if e and p:
                    accounts.append({"email": e, "password": p})
    except Exception as exc:
        log.error(f"Could not load {filename}: {exc}")
    return accounts


def list_all_folders(mail):
    """Return all folder names that exist on the server."""
    status, folder_list = mail.list()
    folders = []
    if status != "OK":
        return folders
    for entry in folder_list:
        decoded = entry.decode() if isinstance(entry, bytes) else entry
        # Folder name is after the last space-quoted separator
        parts = decoded.split('"/"')
        if len(parts) >= 2:
            name = parts[-1].strip().strip('"')
        else:
            name = decoded.split()[-1].strip().strip('"')
        folders.append(name)
    return folders


def delete_warmup_emails_in_folder(mail, folder, warmup_addresses):
    """
    Searches the given folder for any email FROM or TO any warmup address
    and permanently deletes them.
    Returns count of emails deleted.
    """
    try:
        status, _ = mail.select(folder, readonly=False)
        if status != "OK":
            return 0
    except Exception:
        return 0

    deleted = 0
    for addr in warmup_addresses:
        for search_type in ["FROM", "TO"]:
            try:
                status, messages = mail.search(None, f'({search_type} "{addr}")')
                if status != "OK" or not messages[0]:
                    continue
                nums = messages[0].split()
                if not nums:
                    continue
                log.info(
                    f"      [{search_type} {addr}] → {len(nums)} email(s) found. Deleting..."
                )
                for num in nums:
                    mail.store(num, "+FLAGS", "\\Deleted")
                    deleted += 1
            except Exception as exc:
                log.warning(f"      Search error ({search_type} {addr}): {exc}")

    if deleted:
        try:
            mail.expunge()
        except Exception as exc:
            log.warning(f"      Expunge error: {exc}")

    return deleted


def clean_account(account, warmup_addresses):
    email_addr = account["email"]
    password = account["password"]
    imap_host = get_imap_host(email_addr)

    log.info(f"\n{'─'*60}")
    log.info(f"  Cleaning: {email_addr}")
    log.info(f"{'─'*60}")

    total_deleted = 0
    try:
        mail = imaplib.IMAP4_SSL(imap_host)
        mail.login(email_addr, password)

        # Get folders that actually exist on this server
        existing_folders = list_all_folders(mail)
        log.info(f"  Available folders: {existing_folders}")

        # Intersect with the ones we want to clean
        folders_to_clean = []
        for candidate in FOLDERS_TO_CHECK:
            if candidate in existing_folders:
                folders_to_clean.append(candidate)

        if not folders_to_clean:
            # Fallback: clean INBOX + Sent at minimum
            folders_to_clean = ["INBOX"]

        for folder in folders_to_clean:
            log.info(f"  Checking folder: {folder}")
            count = delete_warmup_emails_in_folder(mail, folder, warmup_addresses)
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
    log.info("  WARMUP EMAIL CLEANER")
    log.info("=" * 60)

    accounts = load_accounts()
    if not accounts:
        log.error("No accounts loaded from warmup_accounts.csv. Aborting.")
        return

    # All warmup email addresses — these are the senders/recipients to nuke
    warmup_addresses = [acc["email"] for acc in accounts]

    log.info(f"Loaded {len(accounts)} accounts.")
    log.info(f"Will delete any emails FROM/TO: {warmup_addresses}\n")

    grand_total = 0
    for i, account in enumerate(accounts, 1):
        log.info(f"\n[Account {i}/{len(accounts)}]")
        deleted = clean_account(account, warmup_addresses)
        grand_total += deleted

        # Brief pause between accounts to be polite to servers
        if i < len(accounts):
            log.info(f"  Waiting 5 seconds before next account...")
            time.sleep(5)

    log.info("\n" + "=" * 60)
    log.info(f"  CLEANUP COMPLETE. Total emails deleted: {grand_total}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
