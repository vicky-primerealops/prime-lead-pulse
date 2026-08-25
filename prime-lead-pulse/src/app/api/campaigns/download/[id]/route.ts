import { NextResponse } from 'next/server';
import { supabase } from '@/utils/supabase';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  
  const url = new URL(request.url);
  const token = url.searchParams.get('token');

  if (!token) {
    return new NextResponse('Unauthorized', { status: 401 });
  }

  const { data: { user }, error: authError } = await supabase.auth.getUser(token);
  if (authError || !user) {
    return new NextResponse('Unauthorized', { status: 401 });
  }

  const { data: campaign, error } = await supabase
    .from('campaigns')
    .select('*')
    .eq('id', id)
    .eq('user_id', user.id)
    .single();

  if (error || !campaign) {
    return new NextResponse('Campaign not found', { status: 404 });
  }

  // Generate the Python Script
  const baseUrl = url.origin;
  
  // Format the python script string
  const pythonCode = `
import os
import csv
import uuid
import time
import smtplib
import requests
import getpass
from email.message import EmailMessage
from email.utils import make_msgid
from datetime import datetime

# ==========================================
# Prime Lead Pulse - Campaign Sender
# Campaign: ${campaign.name}
# Generated on: ${new Date().toISOString()}
# ==========================================

CAMPAIGN_ID = "${campaign.id}"
PLATFORM_API_URL = "${baseUrl}"

# User settings
BATCH_SIZE = ${campaign.batch_size}
DELAY_SECONDS = ${campaign.delay_seconds}
CSV_EXPORT_URL = "${campaign.sheet_url}"

EMAIL_SUBJECT = """${campaign.subject}"""
EMAIL_BODY = """${campaign.body}"""

def get_contacts():
    print("Fetching contacts from Google Sheet...")
    try:
        url = CSV_EXPORT_URL
        if "/edit" in url:
            url = url.split("/edit")[0] + "/export?format=csv"
            
        response = requests.get(url)
        response.raise_for_status()
        
        contacts = []
        lines = response.text.splitlines()
        reader = csv.reader(lines)
        headers = next(reader, None)
        
        for row in reader:
            if len(row) >= 2:
                name = row[0].strip()
                email = row[1].strip()
                if name and email:
                    contacts.append({"name": name, "email": email})
        
        print(f"Found {len(contacts)} contacts.")
        return contacts
    except Exception as e:
        print(f"Error fetching Google Sheet: {e}")
        print("Please ensure your Google Sheet link is set to 'Anyone with the link can view'.")
        return []

def register_email_and_get_pixel(sender_email, to_email, subject):
    email_id = str(uuid.uuid4())
    try:
        payload = {
            "campaign_id": CAMPAIGN_ID,
            "sender_email": sender_email,
            "recipient": to_email,
            "subject": subject,
            "email_id": email_id
        }
        res = requests.post(f"{PLATFORM_API_URL}/api/campaigns/register", json=payload)
        if res.status_code == 200:
            current_time = int(time.time() * 1000)
            pixel_url = f"{PLATFORM_API_URL}/api/track/pixel/{email_id}?t={current_time}"
            return f'<img src="{pixel_url}" width="1" height="1" alt="" style="display:none" />'
        else:
            print(f"  Warning: Failed to register tracking for {to_email}")
            return ""
    except Exception as e:
        print(f"  Warning: Failed to generate pixel: {e}")
        return ""

def get_smtp_server(email):
    email_lower = email.lower()
    if "@gmail.com" in email_lower or "@diyflatfee.com" in email_lower:
        return 'smtp.gmail.com', 465
    elif "@secureserver.net" in email_lower or "godaddy" in email_lower:
        return 'smtpout.secureserver.net', 465
    elif "@yahoo.com" in email_lower:
        return 'smtp.mail.yahoo.com', 465
    elif "@outlook.com" in email_lower or "@hotmail.com" in email_lower:
        return 'smtp.office365.com', 587
    return 'smtp.gmail.com', 465

def send_campaign():
    print(f"=== Starting Campaign: {CAMPAIGN_ID} ===")
    
    sender_email = input("Enter your email address: ").strip()
    print("\\nNote: If using Gmail, you MUST use an App Password (not your regular password).")
    print("Generate one at: https://myaccount.google.com/apppasswords")
    app_password = getpass.getpass("Enter your App Password: ").strip()
    
    if not sender_email or not app_password:
        print("Email and password are required. Exiting.")
        return

    contacts = get_contacts()
    if not contacts:
        return
        
    contacts_to_send = contacts[:BATCH_SIZE]
    print(f"\\nPreparing to send {len(contacts_to_send)} emails...")
    
    try:
        host, port = get_smtp_server(sender_email)
        if port == 465:
            server = smtplib.SMTP_SSL(host, port)
        else:
            server = smtplib.SMTP(host, port)
            server.starttls()
            
        server.login(sender_email, app_password)
        print("Successfully logged into SMTP!\\n")
        
        for i, contact in enumerate(contacts_to_send):
            to_name = contact['name']
            to_email = contact['email']
            first_name = to_name.split()[0] if to_name else ""
            
            subject = EMAIL_SUBJECT.replace("{name}", first_name).replace("{first_name}", first_name)
            body_html = EMAIL_BODY.replace("{name}", first_name).replace("{first_name}", first_name)
            body_html = body_html.replace("\\n", "<br>")
            
            # Register in Supabase and inject pixel
            pixel = register_email_and_get_pixel(sender_email, to_email, subject)
            body_html = f"{body_html}<br><br>{pixel}"
            
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = to_email
            msg['Message-ID'] = make_msgid()
            msg.set_content("Please enable HTML to view this email.")
            msg.add_alternative(body_html, subtype='html')
            
            try:
                server.send_message(msg)
                print(f"[{i+1}/{len(contacts_to_send)}] Sent to {to_name} <{to_email}>")
            except Exception as e:
                print(f"[{i+1}/{len(contacts_to_send)}] Failed to send to {to_email}: {e}")
            
            if i < len(contacts_to_send) - 1:
                print(f"Waiting {DELAY_SECONDS} seconds...")
                time.sleep(DELAY_SECONDS)
                
        server.quit()
        print("\\n=== Campaign Sending Complete! ===")
        
    except smtplib.SMTPAuthenticationError:
        print("\\nERROR: Invalid email or App Password.")
    except Exception as e:
        print(f"\\nERROR: An unexpected error occurred: {e}")

if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("Required package 'requests' is not installed.")
        print("Please run: pip install requests")
        exit(1)
    send_campaign()
`;

  return new NextResponse(pythonCode, {
    status: 200,
    headers: {
      'Content-Type': 'application/octet-stream',
      'Content-Disposition': `attachment; filename="plp_campaign_${campaign.id.split('-')[0]}.py"`,
    },
  });
}
