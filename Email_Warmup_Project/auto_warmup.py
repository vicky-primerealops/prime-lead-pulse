import csv
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
log = logging.getLogger(__name__)

SUBJECTS = [
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
    "Morning!", "Checking in on progress"
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
    "Just touching base on this project. Any blockers?",
    "Wanted to quickly loop you in on the latest changes. Let's discuss tomorrow.",
    "Do you have time for a quick call this afternoon?",
    "I reviewed the document you sent over. Let me know when you're free to chat.",
    "Just dropping a quick note to say hi. Hope all is well!",
    "Please ignore my last email, I figured it out.",
    "Can we push our meeting back by 30 minutes? Let me know if that works.",
    "I'm still waiting on a response from the client, I'll update you as soon as I hear back.",
    "Everything is on track for Friday's deadline.",
    "Have a great weekend! See you Monday.",
    "Just a friendly reminder about the forms due next week.",
    "Hope you're having a productive week! I just wanted to circle back on our last conversation.",
    "Let me know if you need any help with the tasks assigned yesterday.",
    "Are you free for lunch sometime next week? It's been a while.",
    "I attached the initial draft for your review. Please let me know what you think.",
    "Can we jump on a quick 5-minute call? I have a question about the process.",
    "I wanted to introduce you to the new workflow we discussed. Details are below.",
    "Just confirming that I received your email. I will process it shortly.",
    "I'm having a bit of trouble with the software login, who should I contact?",
    "Do you know when the updated report will be ready? No rush, just planning my day.",
    "The client loved the presentation. Great job on putting that together!",
    "I'm going to log off a bit early today, but I'll be back online first thing tomorrow.",
    "Just making sure we are aligned on the deliverables for this month.",
    "Thanks for your help with this. I really appreciate it.",
    "I think we need to adjust the timeline slightly. Let's discuss when you have a moment.",
    "Is there any update on the approval process? Let me know.",
    "I'll send over the meeting invite shortly. Look out for it.",
    "Hope you had a great weekend. Ready to tackle this week?",
    "I've cc'd the rest of the team so everyone is in the loop.",
    "Let's touch base on Thursday to review the final numbers.",
    "Can you double-check the figures on page 3? They look a bit off to me."
]

REPLY_BODIES = [
    "Got it, thanks!",
    "Understood, I will get back to you shortly.",
    "Thanks for letting me know. Sounds good.",
    "No problem at all.",
    "Will do. Talk soon!",
    "Perfect, thanks for the update.",
    "Received! Have a great day.",
    "Thanks for the heads up.",
    "Sure thing, I'll take a look.",
    "Makes sense to me.",
    "Okay, I'll keep you posted.",
    "Appreciate the update.",
    "Thanks! I'll review and get back to you.",
    "Got it. Let's touch base later.",
    "Sounds great.",
    "Will check on this and revert.",
    "Noted, thanks.",
    "I'll handle it right away.",
    "Okay, let me know if anything changes.",
    "Thanks for clarifying.",
    "Looking forward to it.",
    "I agree with your points.",
    "Let's go with your suggestion.",
    "I'll let the team know.",
    "Thanks for the quick response.",
    "This works for me.",
    "Awesome, thank you.",
    "I'll add this to my list.",
    "Got the files, thanks.",
    "Perfect timing, thanks."
]

def get_server_info(email_addr):
    # Determines IMAP and SMTP settings based on the email domain
    email_lower = email_addr.lower()
    if "@gmail.com" in email_lower or "@diyflatfee.com" in email_lower:
        return {"imap": "imap.gmail.com", "smtp": "smtp.gmail.com", "port": 465}
    else:
        # Defaults to GoDaddy settings for info@primerealops.com
        return {"imap": "imap.secureserver.net", "smtp": "smtpout.secureserver.net", "port": 465}

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
    except Exception as e:
        log.error(f"Error loading {filename}: {e}")
    return accounts

def process_inbox_and_spam(account, all_emails):
    email_addr = account['email']
    password = account['password']
    server_info = get_server_info(email_addr)
    
    try:
        log.info(f"[{email_addr}] Connecting to IMAP to check Spam and Inbox...")
        mail = imaplib.IMAP4_SSL(server_info["imap"])
        mail.login(email_addr, password)
        
        # 1. FIND SPAM FOLDER AND MOVE WARMUP EMAILS TO INBOX
        status, folders = mail.list()
        spam_folder = None
        for f in folders:
            f_lower = f.lower()
            if b'spam' in f_lower or b'junk' in f_lower:
                spam_folder = f.decode().split(' "/" ')[-1]
                break
                
        if spam_folder:
            mail.select(spam_folder)
            for sender in all_emails:
                if sender == email_addr: continue
                # We strictly only search for emails FROM the other accounts in our CSV
                status, messages = mail.search(None, f'(FROM "{sender}")')
                if status == "OK" and messages[0]:
                    nums = messages[0].split()
                    if nums:
                        log.info(f"[{email_addr}] Found {len(nums)} warmup emails in SPAM. Moving to Inbox...")
                    for num in nums:
                        mail.copy(num, "INBOX")
                        mail.store(num, '+FLAGS', '\\Deleted')
            mail.expunge()
        
        # 2. Reply to unread warmup emails
        mail.select("INBOX")
        replies_sent = 0
        max_replies = random.randint(8, 10)
        
        for sender in all_emails:
            if sender == email_addr: continue
            # Strictly only reply to UNSEEN emails from other accounts in our CSV
            status, messages = mail.search(None, f'(UNSEEN FROM "{sender}")')
            if status == "OK" and messages[0]:
                nums = messages[0].split()
                for num in nums:
                    if replies_sent < max_replies: # Limit replies per account per run to avoid spamming
                        typ, data = mail.fetch(num, '(RFC822)')
                        raw_email = data[0][1]
                        msg = email.message_from_bytes(raw_email)
                        msg_id = msg.get("Message-ID")
                        subject = msg.get("Subject", "")
                        if not subject.lower().startswith("re:"):
                            subject = "Re: " + subject
                            
                        # Send Reply
                        send_reply(account, sender, subject, msg_id)
                        replies_sent += 1
                        time.sleep(random.randint(15, 30))
                        
                    # Mark as read
                    mail.store(num, '+FLAGS', '\\Seen')
                    
        mail.close()
        mail.logout()
    except Exception as e:
        log.error(f"[{email_addr}] IMAP error: {e}")

def send_reply(account, to_email, subject, in_reply_to):
    server_info = get_server_info(account['email'])
    try:
        with smtplib.SMTP_SSL(server_info["smtp"], server_info["port"]) as server:
            server.login(account['email'], account['password'])
            body = random.choice(REPLY_BODIES)
            msg = MIMEMultipart()
            msg["Subject"] = subject
            msg["From"] = account['email']
            msg["To"] = to_email
            msg["In-Reply-To"] = in_reply_to
            msg["References"] = in_reply_to
            msg["X-Warmup-Email"] = "True"  # Hidden signature for safe deletion
            
            msg.attach(MIMEText(body, "plain"))
            server.send_message(msg)
            log.info(f"    -> Sent REPLY to {to_email}")
    except Exception as e:
        log.error(f"Failed to reply from {account['email']}: {e}")

def send_new_emails(account, all_emails):
    sender_email = account["email"]
    sender_pass = account["password"]
    server_info = get_server_info(sender_email)
    
    num_to_send = random.randint(12, 18)
    possible_receivers = [e for e in all_emails if e != sender_email]
    num_to_send = min(num_to_send, len(possible_receivers))
    receivers = random.sample(possible_receivers, num_to_send)

    log.info(f"[{sender_email}] Sending NEW emails to {len(receivers)} colleagues.")

    try:
        with smtplib.SMTP_SSL(server_info["smtp"], server_info["port"]) as server:
            server.login(sender_email, sender_pass)
            for receiver in receivers:
                subject = random.choice(SUBJECTS)
                body = random.choice(BODIES)
                
                msg = MIMEMultipart()
                msg["From"] = sender_email
                msg["To"] = receiver
                msg["Subject"] = subject
                msg["X-Warmup-Email"] = "True"  # Hidden signature for safe deletion
                
                msg.attach(MIMEText(body, "plain"))
                
                server.send_message(msg)
                log.info(f"    -> Sent email to {receiver}")
                time.sleep(random.randint(30, 90))
    except Exception as e:
        log.error(f"Failed to send from {sender_email}: {e}")


def main():
    log.info("Starting Auto Email Warmup Script (Includes Replies & Unspamming)...")
    accounts = load_accounts()
    
    if not accounts:
        log.error("No accounts loaded. Aborting.")
        return

    all_email_addresses = [acc["email"] for acc in accounts]
    log.info(f"Loaded {len(accounts)} accounts. Randomizing order...")
    random.shuffle(accounts)

    for account in accounts:
        # Step 1: Login via IMAP -> Move Spam to Inbox -> Reply to Unread
        process_inbox_and_spam(account, all_email_addresses)
        
        # Step 2: Login via SMTP -> Send New Emails
        send_new_emails(account, all_email_addresses)

        # Pause heavily before logging into the next account
        next_delay = random.randint(60, 150)
        log.info(f"Finished processing {account['email']}. Waiting {next_delay}s before next account...")
        time.sleep(next_delay)
        
    log.info("Warmup sequence complete for today. Good job!")

if __name__ == "__main__":
    main()
