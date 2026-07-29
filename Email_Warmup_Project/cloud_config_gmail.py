import os

# ── Google Sheets ────────────────────────────────────────────────────
SERVICE_ACCOUNT_FILE = "service_account.json"
SPREADSHEET_ID       = os.environ["SPREADSHEET_ID"]

# ── Gmail SMTP settings ─────────────────────────────────────────────
SMTP_HOST            = "smtp.gmail.com"
SMTP_PORT            = 465
SMTP_USER            = os.environ["GMAIL_USER"]
SMTP_PASSWORD        = os.environ["GMAIL_APP_PASSWORD"]
SMTP_USER_2          = os.environ.get("GMAIL_USER_2", "")
SMTP_PASSWORD_2      = os.environ.get("GMAIL_APP_PASSWORD_2", "")
FROM_NAME            = os.environ.get("FROM_NAME", "Vicky Thakkar")
SEND_DELAY_SECONDS   = 120
