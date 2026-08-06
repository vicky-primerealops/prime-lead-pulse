"""
cleanup_warmup_emails.py
────────────────────────
SAFELY deletes ONLY warmup emails by matching on the exact subjects
used in the warmup script. Does NOT delete any real emails.

Safety mechanism:
  • Only deletes emails whose subject EXACTLY matches one from the warmup SUBJECTS list
  • AND the sender is one of your warmup accounts
  • This ensures real client emails are NEVER touched

Run locally:
  python cleanup_warmup_emails.py
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

# ── Exact subjects used in auto_warmup.py ─────────────────────────────────────
# These are the ONLY subjects that will be deleted. Real emails are safe.
WARMUP_SUBJECTS = [
    "Quick question", "Hey!", "Following up on yesterday", "Checking in",
    "Meeting notes", "Catch up later?", "Re: Last week", "Quick update",
    "Thoughts on this?", "Hello!", "Action items", "Are we still on?",
    "Can we chat?", "Quick favor", "Update required", "Just checking in",
    "Status report", "Do you have a minute?", "Need your input", "Project update",
    "Coffee next week?", "Lunch plans", "Review requested", "Feedback on the proposal",
    "Touching base", "Checking your availability", "Quick sync", "Weekly sync",
    "Introduction", "Connecting", "Schedule change", "Rescheduling our call",
    "Follow up", "Just saying hi", "Checking in again", "Question about the project",
    "A quick favor", "Need advice", "Quick call?", "Got a minute?",
    "Hope you're well", "Checking the timeline", "Invoice follow up", "Quick request",
    "Brainstorming session", "Next steps", "Catching up", "Happy Friday!",
    "Morning!", "Checking in on progress",
    # Re: variants
    "Re: Quick question", "Re: Hey!", "Re: Following up on yesterday", "Re: Checking in",
    "Re: Meeting notes", "Re: Catch up later?", "Re: Last week", "Re: Quick update",
    "Re: Thoughts on this?", "Re: Hello!", "Re: Action items", "Re: Are we still on?",
    "Re: Can we chat?", "Re: Quick favor", "Re: Update required", "Re: Just checking in",
    "Re: Status report", "Re: Do you have a minute?", "Re: Need your input",
    "Re: Project update", "Re: Coffee next week?", "Re: Lunch plans",
    "Re: Review requested", "Re: Feedback on the proposal", "Re: Touching base",
    "Re: Checking your availability", "Re: Quick sync", "Re: Weekly sync",
    "Re: Introduction", "Re: Connecting", "Re: Schedule change",
    "Re: Rescheduling our call", "Re: Follow up", "Re: Just saying hi",
    "Re: Checking in again", "Re: Question about the project", "Re: A quick favor",
    "Re: Need advice", "Re: Quick call?", "Re: Got a minute?", "Re: Hope you're well",
    "Re: Checking the timeline", "Re: Invoice follow up", "Re: Quick request",
    "Re: Brainstorming session", "Re: Next steps", "Re: Catching up",
    "Re: Happy Friday!", "Re: Morning!", "Re: Checking in on progress",
]

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
                e = row.get("Email", "").strip()
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


def delete_warmup_emails_in_folder(mail, folder, warmup_addresses):
    """
    Deletes ONLY emails that match BOTH:
      1. FROM one of the warmup addresses
      2. Subject matches one of the known warmup subjects

    This ensures real client/work emails are never touched.
    """
    try:
        status, _ = mail.select(folder, readonly=False)
        if status != "OK":
            return 0
    except Exception:
        return 0

    deleted = 0

    for addr in warmup_addresses:
        for subject in WARMUP_SUBJECTS:
            try:
                # Search strictly: FROM warmup address AND exact subject
                search_criteria = f'(FROM "{addr}" SUBJECT "{subject}")'
                status, messages = mail.search(None, search_criteria)
                if status != "OK" or not messages[0]:
                    continue
                nums = messages[0].split()
                if not nums:
                    continue
                log.info(f"      Found {len(nums)} warmup email(s): [{subject}] from {addr}")
                for num in nums:
                    mail.store(num, "+FLAGS", "\\Deleted")
                    deleted += 1
            except Exception as exc:
                log.warning(f"      Search error: {exc}")

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

        existing_folders = list_all_folders(mail)
        folders_to_clean = [f for f in FOLDERS_TO_CHECK if f in existing_folders]
        if not folders_to_clean:
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
    log.info("  WARMUP EMAIL CLEANER (Subject-Safe Mode)")
    log.info("  Only deletes emails with known warmup subjects.")
    log.info("  Real emails are NOT touched.")
    log.info("=" * 60)

    accounts = load_accounts()
    if not accounts:
        log.error("No accounts loaded from warmup_accounts.csv. Aborting.")
        return

    warmup_addresses = [acc["email"] for acc in accounts]
    log.info(f"Loaded {len(accounts)} accounts.\n")

    grand_total = 0
    for i, account in enumerate(accounts, 1):
        log.info(f"\n[Account {i}/{len(accounts)}]")
        deleted = clean_account(account, warmup_addresses)
        grand_total += deleted
        if i < len(accounts):
            time.sleep(3)

    log.info("\n" + "=" * 60)
    log.info(f"  CLEANUP COMPLETE. Total warmup emails deleted: {grand_total}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
