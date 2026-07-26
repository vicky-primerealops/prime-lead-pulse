import csv
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
import random
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
log = logging.getLogger(__name__)

FRIENDS_EMAILS = [
    "shivanisabby@gmail.com", "khanaltmesh@gmail.com", "simransabnani20@gmail.com",
    "riddhisabby@gmail.com", "nareshodc1619@gmail.com", "shivani@code-b.in",
    "shivani.subnani@ves.ac.in", "altmesh@techacadium.com", "shivani@techacadium.com",
    "narsim2212@gmail.com", "pavansabnani@gmail.com", "mishtisabby@gmail.com",
    "helloaltmesh@gmail.com", "khantoshifa@gmail.com", "deepa.thakkar@here.com"
]

OPEN_ENDED_REPLIES = [
    "By the way, how have things been on your end lately?",
    "What are you working on these days?",
    "Any fun plans for the upcoming weekend?",
    "How is everything going with work?",
    "Are you still working on the same projects as before?",
    "It's been a while, what's new with you?",
    "I'd love to hear what you've been up to recently!",
    "How are things holding up on your side?",
    "Got any exciting updates on your end?"
]

def get_server_info(email_addr):
    email_lower = email_addr.lower()
    if "@gmail.com" in email_lower or "@diyflatfee.com" in email_lower:
        return {"imap": "imap.gmail.com", "smtp": "smtp.gmail.com", "port": 465}
    else:
        return {"imap": "imap.secureserver.net", "smtp": "smtpout.secureserver.net", "port": 465}

def load_accounts(filename="warmup_accounts.csv"):
    accounts = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                e = row.get("Email", "").strip()
                p = row.get("AppPassword", "").strip()
                if e and p and e.lower() != "vickythakkar6143@gmail.com":
                    accounts.append({"email": e, "password": p})
    except Exception as e:
        log.error(f"Error loading {filename}: {e}")
    return accounts

def main():
    log.info("Scanning for friends' replies...")
    accounts = load_accounts()
    if not accounts: 
        return
    
    unique_friends = list(set(FRIENDS_EMAILS))
    
    for account in accounts:
        email_addr = account["email"]
        password = account["password"]
        server_info = get_server_info(email_addr)
        
        try:
            log.info(f"[{email_addr}] Checking inbox...")
            mail = imaplib.IMAP4_SSL(server_info["imap"])
            mail.login(email_addr, password)
            mail.select("INBOX")
            
            for friend in unique_friends:
                # Search for UNREAD emails specifically from the friend
                status, messages = mail.search(None, f'(UNSEEN FROM "{friend}")')
                if status == "OK" and messages[0]:
                    for num in messages[0].split():
                        typ, data = mail.fetch(num, '(RFC822)')
                        raw_email = data[0][1]
                        msg = email.message_from_bytes(raw_email)
                        
                        msg_id = msg.get("Message-ID")
                        subject = msg.get("Subject", "")
                        if not subject.lower().startswith("re:"):
                            subject = "Re: " + subject
                            
                        # Send the auto-reply with an open-ended question
                        with smtplib.SMTP_SSL(server_info["smtp"], server_info["port"]) as server:
                            server.login(email_addr, password)
                            body = "Got it, thanks! \n\n" + random.choice(OPEN_ENDED_REPLIES)
                            reply_msg = MIMEText(body)
                            reply_msg["Subject"] = subject
                            reply_msg["From"] = email_addr
                            reply_msg["To"] = friend
                            if msg_id:
                                reply_msg["In-Reply-To"] = msg_id
                                reply_msg["References"] = msg_id
                            
                            server.send_message(reply_msg)
                            log.info(f"    -> Auto-replied to {friend} with a question!")
                            
                        # Mark as read so we don't reply to it again
                        mail.store(num, '+FLAGS', '\\Seen')
                        time.sleep(random.randint(5, 10))
                        
            mail.close()
            mail.logout()
        except Exception as e:
            log.error(f"[{email_addr}] Error checking mail: {e}")

    log.info("Finished scanning all accounts.")

if __name__ == "__main__":
    main()
