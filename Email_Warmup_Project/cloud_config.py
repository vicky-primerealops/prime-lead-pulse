# cloud_config.py
# ================
# This file is committed to GitHub. It has NO hardcoded secrets.
# All values come from GitHub Secrets injected as environment variables.
# The workflow copies this file to config.py before running send_emails.py.

import os

SERVICE_ACCOUNT_FILE = "service_account.json"
SPREADSHEET_ID       = os.environ["SPREADSHEET_ID"]
SHEET_RANGE          = "Sheet1!A2:B"
SMTP_HOST            = os.environ["SMTP_HOST"]
SMTP_PORT            = int(os.environ["SMTP_PORT"])
SMTP_USER            = os.environ["SMTP_USER"]
SMTP_PASSWORD        = os.environ["SMTP_PASSWORD"]
FROM_NAME            = os.environ.get("FROM_NAME", "Prime Real Ops")
SEND_DELAY_SECONDS   = 120
