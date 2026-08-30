import sys
from cleanup_warmup_emails import load_accounts, clean_account
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

accounts = load_accounts()
warmup_set = set(acc["email"] for acc in accounts)
info_acc = next(acc for acc in accounts if acc["email"] == "info@primerealops.com")
clean_account(info_acc, warmup_set)
