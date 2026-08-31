import random
import os
import time
import logging
import smtplib
import email.policy
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ==========================================
# PRIME LEAD PULSE TRACKING CONFIGURATION
# ==========================================
SUPABASE_URL = "https://ciihhdpjeklpqgpmrocm.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNpaWhoZHBqZWtscHFncG1yb2NtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NzQ4ODYzOCwiZXhwIjoyMTAzMDY0NjM4fQ.EoH-jDiQsy4TAIIlIFQ9j4yhiLsYlAsAIwC6F0yOYqQ"
USER_ID = "254c62d5-7e74-4dd4-b74d-f9685b00ac10"
# ==========================================

# ── Configuration ─────────────────────────────────────────────────────────────
# Update this with the Google Sheet ID where you'll paste the Zillow data
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "1tIw9dA3ENNyZl8FJ3tuM6zrwhZwwOEj0ljL15SbspQk")
SERVICE_ACCOUNT_FILE = "service_account.json"

# Sending account details
SENDER_EMAIL = "vicky@diyflatfee.com"  # Update if using a different account
SENDER_PASSWORD = "edcsdjffxnjtkgkl"  # App password for the sending account

# ── Logging Setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)5s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Email Content ─────────────────────────────────────────────────────────────
EMAIL_SUBJECT = "Partnership for Flat Fee MLS Listings in {state}"

def generate_spun_content(to_name, state):
    greetings = [
        f"Hi {to_name},",
        f"Hello {to_name},",
        f"Hey {to_name},",
        f"Good morning {to_name},"
    ]
    
    openers = [
        f"I'm reaching out because DIY Realty™ is transitioning our model and we are looking for a reliable partner broker in {state} to handle our Flat Fee MLS listings.",
        f"I'm contacting you today because DIY Realty™ is shifting our operational model, and we are searching for a dependable partner broker in {state} for our Flat Fee MLS listings.",
        f"My name is Vicky and our brokerage is currently expanding our flat fee model. We're looking for a trusted partner broker in {state} to manage our MLS listings.",
        f"I am getting in touch because DIY Realty™ is updating its business model, and we need a reliable real estate partner in {state} to help process our Flat Fee MLS listings."
    ]
    
    pitches = [
        "We pay a standard upfront fee of $150 for every MLS entry you process for our clients. This is a risk-free way to add a steady stream of listings to your pipeline with zero marketing cost or effort on your end.",
        "Our standard payout is $150 upfront for each MLS entry you handle for our sellers. It's a completely risk-free method to increase your listing inventory without spending any time or money on marketing.",
        "We compensate our partners with a flat $150 upfront for every listing entered into the MLS for our clients. It's a great, risk-free opportunity to build your pipeline with absolutely zero marketing spend on your part.",
        "You'll receive a guaranteed $150 upfront for every MLS listing you process on behalf of our clients. This gives you a consistent flow of new listings with zero customer acquisition costs."
    ]
    
    ctas = [
        "If you are open to discussing this, I would love to get on a brief call to see if we'd be a good fit.",
        "If this sounds interesting to you, I'd love to schedule a quick call to see if there's a mutual fit.",
        "If you're open to a potential partnership, I would appreciate a brief conversation to explore this further.",
        "Should this align with your business goals, I'd love to connect on a short call to discuss a potential fit."
    ]
    
    signoffs = [
        "Best Regards,",
        "Best,",
        "Thanks,",
        "Thanks in advance,"
    ]
    
    return {
        "greeting": random.choice(greetings),
        "opener": random.choice(openers),
        "pitch": random.choice(pitches),
        "cta": random.choice(ctas),
        "signoff": random.choice(signoffs)
    }

def get_email_body_text(spun):
    return f"""\
{spun['greeting']}

{spun['opener']}

{spun['pitch']}

{spun['cta']}

You can click here to book a quick chat at a time that works best for you: https://calendar.app.google/JmdT2Xqs2nM17zw99

{spun['signoff']}

Vicky Thakkar
Operations | DIY Realty™
America's Leading FlatFee MLS Brokerage
(888) 601-3771 | (859) 209-6868
diyflatfee.com
Support@DIYFlatFee.com | Vicky@DIYFlatFee.com
1040 Monarch Street, Suite 300, Lexington, KY 40513
"""

def get_email_body_html(spun, tracking_pixel=""):
    return f"""\
<!DOCTYPE html>
<html>
<head>
<style>
  .body-text {{ font-family: Arial, Helvetica, sans-serif; color: #333333; line-height: 1.6; font-size: 15px; }}
  .sig-text {{ font-family: Arial, Helvetica, sans-serif; color: #333333; font-size: 13px; line-height: 1.5; }}
  .blue-link {{ color: #0056b3; text-decoration: underline; font-weight: bold; }}
</style>
</head>
<body style="margin: 0; padding: 0;">

  <div class="body-text">
    <p style="margin-bottom: 20px;">{spun['greeting']}</p>

    <p style="margin-bottom: 20px;">{spun['opener']}</p>

    <p style="margin-bottom: 20px;">{spun['pitch']}</p>

    <p style="margin-bottom: 20px;">{spun['cta']}</p>

    <p style="margin-bottom: 40px;">You can <strong><a href="https://calendar.app.google/JmdT2Xqs2nM17zw99" class="blue-link">click here to book a quick chat</a></strong> at a time that works best for you.</p>
  </div>

  <div class="sig-text">
    <p style="margin: 0; margin-bottom: 25px;">{spun['signoff']}</p>
    
    <p style="margin: 0 0 4px 0; font-size: 18px; font-weight: bold; color: #111111;">Vicky Thakkar</p>
    <p style="margin: 0 0 2px 0; font-weight: 700; color: #333333;">Operations | <strong>DIY Realty&trade;</strong></p>
    <p style="margin: 0 0 15px 0; font-weight: 700; color: #333333;">America's Leading FlatFee MLS Brokerage</p>
    
    <p style="margin: 0 0 10px 0; color: #333333;">
      <span style="font-size: 14px;">&#9742;&#65039;</span> (888) 601-3771 &nbsp;|&nbsp; <span style="font-size: 14px;">&#128241;</span> (859) 209-6868
    </p>
    
    <p style="margin: 0 0 10px 0;">
      <span style="font-size: 15px;">&#127760;</span> <a href="https://diyflatfee.com" style="color: #333333; text-decoration: none; font-weight: 500;">diyflatfee.com</a>
    </p>
    
    <p style="margin: 0 0 10px 0;">
      <span style="font-size: 14px;">&#9993;&#65039;</span> <a href="mailto:Support@DIYFlatFee.com" style="color: #333333; text-decoration: none; font-weight: 500;">Support@DIYFlatFee.com</a> &nbsp;|&nbsp; <a href="mailto:Vicky@DIYFlatFee.com" style="color: #333333; text-decoration: none; font-weight: 500;">Vicky@DIYFlatFee.com</a>
    </p>
    
    <p style="margin: 0 0 10px 0; color: #333333;">
      <span style="font-size: 15px;">&#128205;</span> 1040 Monarch Street, Suite 300, Lexington, KY 40513
    </p>
  </div>
  
  <!-- INJECT PRIME LEAD PULSE TRACKING PIXEL HERE -->
  {tracking_pixel}

</body>
</html>
"""

def register_email_in_tracker(to_email, subject, from_user):
    """
    Registers the email in your Prime Lead Pulse database 
    and returns the tracking pixel HTML to inject.
    """
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    data = {
        "user_id": USER_ID,
        "sender_email": from_user,
        "recipient": to_email,
        "subject": subject
    }
    
    for attempt in range(3):
        try:
            response = requests.post(f"{SUPABASE_URL}/rest/v1/emails", headers=headers, json=data)
            response.raise_for_status()
            # Get the UUID of the newly created email
            email_id = response.json()[0]["id"]
            
            # Return the invisible tracking pixel
            return f'<img src="https://prime-lead-pulse.vercel.app/api/track/pixel/{email_id}" width="1" height="1" style="display:none;" />'
        except Exception as e:
            if attempt < 2:
                log.warning(f"Tracker registration failed ({e}). Retrying in 1s...")
                time.sleep(1)
            else:
                log.error(f"Failed to register email with tracker after 3 attempts: {e}")
                return "" # If it fails, return nothing so the email still sends

def build_message(to_name, to_email, location_state, from_user):
    # Extract just the first name for a casual greeting
    first_name = to_name.split()[0]
    
    subject = EMAIL_SUBJECT.format(state=location_state)
    
    # 1. Register the email with Prime Lead Pulse to get the Pixel HTML
    pixel_html = register_email_in_tracker(to_email, subject, from_user)
    
    # 2. Generate Spintax content
    spun = generate_spun_content(first_name, location_state)
    
    # 3. Create invisible watermark to break fingerprinting
    import string
    unique_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    invisible_watermark = f'<div style="display:none; color:transparent; opacity:0; font-size:0px; height:0px; width:0px; overflow:hidden;">System Ref {unique_id} - {random.randint(10000, 99999)}</div>'
    
    body_text = get_email_body_text(spun)
    
    # 4. Inject the pixel AND the invisible watermark into the HTML body
    body_html = get_email_body_html(spun, tracking_pixel=pixel_html + "\n" + invisible_watermark)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Vicky Thakkar <{from_user}>"
    msg["To"] = to_email
    
    msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(body_html, "html"))
    return msg


def get_contacts_from_sheet():
    """
    Reads the Google Sheet. Expects the full Zillow CSV export:
    A (0): Agent Name
    G (6): Email
    I (8): State
    M (12): Sent Status (Script writes timestamp here)
    """
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=scopes
    )
    service = build("sheets", "v4", credentials=creds)
    
    # Add resilience for temporary network blips
    for attempt in range(3):
        try:
            result = (
                service.spreadsheets()
                .values()
                .get(spreadsheetId=SPREADSHEET_ID, range="Sheet1!A2:M")
                .execute()
            )
            break
        except Exception as e:
            if attempt < 2:
                import time
                log.warning(f"Network error connecting to Google Sheets. Retrying in 5s... ({e})")
                time.sleep(5)
            else:
                log.error("Failed to fetch Google Sheet after 3 attempts.")
                raise e
    
    rows = result.get("values", [])
    contacts = []
    
    for i, row in enumerate(rows, start=2):
        if len(row) < 7:  # Need at least up to Email (column G / index 6)
            continue
            
        name = row[0].strip() if len(row) > 0 else ""
        email = row[6].strip() if len(row) > 6 else ""
        
        # State is in Column I (index 8)
        state = row[8].strip() if len(row) > 8 else "your area"
        
        # Sent Status is in Column M (index 12)
        sent_status = row[12].strip() if len(row) > 12 else ""
        
        if sent_status:  # Skip already sent
            continue
            
        if name and email and "@" in email:
            contacts.append({
                "name": name, 
                "email": email, 
                "state": state, 
                "row": i
            })
            
    return contacts, service

def mark_as_sent(service, row):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for attempt in range(3):
        try:
            service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=f"Sheet1!M{row}",
                valueInputOption="RAW",
                body={"values": [[timestamp]]},
            ).execute()
            break
        except Exception as e:
            if attempt < 2:
                import time
                time.sleep(5)
            else:
                log.error(f"Failed to update sheet for row {row}: {e}")

MAX_EMAILS_PER_RUN = 75

def send_diy_outreach():
    log.info("Starting DIY Flat Fee MLS outreach campaign...")
    
    contacts, service = get_contacts_from_sheet()
    
    if not contacts:
        log.info("No new contacts to email. Exiting.")
        return
        
    if len(contacts) > MAX_EMAILS_PER_RUN:
        log.info(f"Found {len(contacts)} pending brokers. Limiting to {MAX_EMAILS_PER_RUN} for this run to protect sender reputation.")
        contacts = contacts[:MAX_EMAILS_PER_RUN]
    else:
        log.info(f"Found {len(contacts)} pending brokers to contact.")
    
    smtp_host = "smtp.gmail.com" if "gmail" in SENDER_EMAIL or "diyflatfee" in SENDER_EMAIL else "smtpout.secureserver.net"
    smtp_port = 465
    
    for idx, contact in enumerate(contacts):
        try:
            msg = build_message(
                to_name=contact["name"], 
                to_email=contact["email"], 
                location_state=contact["state"],
                from_user=SENDER_EMAIL
            )
            
            # Open a fresh connection for each email to prevent idle timeouts from Google
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            
            # Mark as sent in Google Sheets
            mark_as_sent(service, contact["row"])
            
            log.info(f"✓ Sent ({idx+1}/{len(contacts)}) -> {contact['name']} <{contact['email']}>")
            
            # Add delay between emails to protect sender reputation
            if idx < len(contacts) - 1:
                import random
                delay = random.randint(35, 60)
                log.info(f"Waiting {delay}s before next email...")
                time.sleep(delay)
                
        except Exception as e:
            log.error(f"Failed to send to {contact['email']}: {e}")
            
        # Baseline delay to prevent hammering APIs on rapid failures or loop exit
        time.sleep(1.5)

    log.info("Outreach campaign completed.")

if __name__ == "__main__":
    send_diy_outreach()
