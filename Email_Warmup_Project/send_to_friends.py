import csv
import smtplib
from email.mime.text import MIMEText
import time
import random
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
log = logging.getLogger(__name__)

# List of friends extracted from the screenshot
FRIENDS_EMAILS = [
    "shivanisabby@gmail.com",
    "khanaltmesh@gmail.com",
    "simransabnani20@gmail.com",
    "riddhisabby@gmail.com",
    "nareshodc1619@gmail.com",
    "shivani@code-b.in",
    "shivani.subnani@ves.ac.in",
    "altmesh@techacadium.com",
    "shivani@techacadium.com",
    "narsim2212@gmail.com",
    "pavansabnani@gmail.com",
    "mishtisabby@gmail.com",
    "helloaltmesh@gmail.com",
    "deepa.thakkar@here.com"
]

SUBJECT = "Just following up! / Checking in"

def get_body(friend_email):
    # Try to extract a first name for a personal touch, or default to a generic greeting
    name_part = friend_email.split("@")[0]
    name = ''.join(c for c in name_part if c.isalpha()).capitalize()
    if not name:
        name = "there"
        
    return f"""Hi {name},

Hope everything has been going well since we last spoke!

I am doing a follow-up test on my new email setup to make sure my responses are getting through properly and not landing in spam.

Could you drop a quick reply letting me know what you've been up to lately, or any fun plans you have for the upcoming weekend? Having a quick back-and-forth conversation helps a ton with my email score.

Thanks again for all the help!

Best Regards,"""

def get_server_info(email_addr):
    email_lower = email_addr.lower()
    if "@gmail.com" in email_lower or "@diyflatfee.com" in email_lower:
        return {"smtp": "smtp.gmail.com", "port": 465}
    else:
        return {"smtp": "smtpout.secureserver.net", "port": 465}

def load_senders(filename="warmup_accounts.csv"):
    accounts = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                e = row.get("Email", "").strip()
                p = row.get("AppPassword", "").strip()
                if e and p:
                    # Exclude the specific email requested
                    if e.lower() != "vickythakkar6143@gmail.com":
                        accounts.append({"email": e, "password": p})
    except Exception as e:
        log.error(f"Error loading {filename}: {e}")
    return accounts

def main():
    log.info("Starting Friends Email Blast...")
    senders = load_senders()
    
    if not senders:
        log.error("No sender accounts loaded.")
        return
        
    log.info(f"Loaded {len(senders)} senders (vickythakkar6143 excluded).")
    
    # Removing duplicates (like mishtisabby@gmail.com which appeared twice)
    unique_friends = list(set(FRIENDS_EMAILS))
    
    for sender in senders:
        sender_email = sender["email"]
        sender_pass = sender["password"]
        server_info = get_server_info(sender_email)
        
        log.info(f"[{sender_email}] Connecting to send to {len(unique_friends)} friends...")
        try:
            with smtplib.SMTP_SSL(server_info["smtp"], server_info["port"]) as server:
                server.login(sender_email, sender_pass)
                
                for friend in unique_friends: 
                    msg = MIMEText(get_body(friend))
                    msg["Subject"] = SUBJECT
                    msg["From"] = sender_email
                    msg["To"] = friend
                    
                    server.send_message(msg)
                    log.info(f"    -> Sent email to {friend}")
                    
                    # Pause 10-20 seconds between sends so Google doesn't block the rapid blast
                    time.sleep(random.randint(10, 20))
                    
        except Exception as e:
            log.error(f"Failed to send from {sender_email}: {e}")
            
        # Pause before switching to the next sender account
        delay = random.randint(30, 60)
        log.info(f"Pausing {delay} seconds before next account...")
        time.sleep(delay)

    log.info("Finished sending emails to all friends!")

if __name__ == "__main__":
    main()
