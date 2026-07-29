import csv
import smtplib
import random
import time
from email.mime.text import MIMEText
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
log = logging.getLogger(__name__)

SUBJECTS = [
    "Checking in", "Quick question", "Meeting notes", "Catch up later?",
    "Re: Last week", "Quick update", "Thoughts on this?", "Hello!",
    "Following up", "Can we chat?", "Action items"
]

BODIES = [
    "Hey, just wanted to check if you got my previous message. Let me know!",
    "Are we still on for the meeting later this week? Confirming the time.",
    "Can you send over those files when you have a moment? No rush.",
    "Hope you are having a good week. Let's catch up soon.",
    "Just a quick update on my end: everything is proceeding as planned.",
    "Did you see the latest email from the team? Wanted to get your thoughts.",
    "I'll be out of the office for a bit later today. Let's connect tomorrow.",
    "Thanks for the update. Looks good to me.",
    "Could you clarify the second point in your last message? Thanks.",
    "Just touching base on this project. Any blockers?"
]

def load_accounts(filename="warmup_accounts.csv"):
    accounts = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Strip whitespace just in case
                email = row.get("Email", "").strip()
                password = row.get("AppPassword", "").strip()
                if email and password:
                    accounts.append({"email": email, "password": password})
    except FileNotFoundError:
        log.error(f"Could not find {filename}. Please ensure it is in the same folder.")
    return accounts

def main():
    log.info("Starting Day 1 Email Warmup Script...")
    accounts = load_accounts()
    
    if not accounts:
        log.error("No accounts loaded. Aborting.")
        return

    log.info(f"Loaded {len(accounts)} accounts. Randomizing sender order...")
    random.shuffle(accounts)

    for sender in accounts:
        sender_email = sender["email"]
        sender_pass = sender["password"]

        # Week 1 PDF guidelines: 5-10 emails per day. Let's do 5-8 random sends.
        num_to_send = random.randint(5, 8)
        
        # Exclude the sender from the receiver pool
        possible_receivers = [acc["email"] for acc in accounts if acc["email"] != sender_email]
        
        # If we have fewer receivers than num_to_send, adjust
        num_to_send = min(num_to_send, len(possible_receivers))
        receivers = random.sample(possible_receivers, num_to_send)

        log.info(f"==> Account {sender_email} is warming up. Sending to {len(receivers)} colleagues.")

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_pass)
                
                for receiver in receivers:
                    subject = random.choice(SUBJECTS)
                    body = random.choice(BODIES)
                    
                    msg = MIMEText(body)
                    msg["Subject"] = subject
                    msg["From"] = sender_email
                    msg["To"] = receiver
                    
                    server.send_message(msg)
                    log.info(f"    -> Sent email to {receiver}")
                    
                    # Pause between individual emails to simulate human typing
                    delay = random.randint(30, 90)
                    log.debug(f"    Sleeping for {delay} seconds...")
                    time.sleep(delay)
                    
        except Exception as e:
            log.error(f"Failed to process sender {sender_email}. Error: {e}")

        # Pause heavily before logging into the next account
        next_sender_delay = random.randint(60, 150)
        log.info(f"Finished sending for {sender_email}. Waiting {next_sender_delay}s before next account...")
        time.sleep(next_sender_delay)
        
    log.info("Warmup sequence complete for today. Good job!")

if __name__ == "__main__":
    main()
