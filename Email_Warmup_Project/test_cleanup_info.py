import sys
import imaplib
from cleanup_warmup_emails import load_accounts
import logging

logging.basicConfig(level=logging.INFO)

accounts = load_accounts()
info_acc = next(acc for acc in accounts if acc["email"] == "info@primerealops.com")

try:
    mail = imaplib.IMAP4_SSL("imap.secureserver.net")
    mail.login(info_acc["email"], info_acc["password"])
    logging.info("Login SUCCESS with imap.secureserver.net")
except Exception as e:
    logging.error(f"Login failed: {e}")

