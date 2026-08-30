import smtplib
import email.policy
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email Content (same as send_diy_outreach.py)
EMAIL_SUBJECT = "Partnership for Flat Fee MLS Listings in {state}"

EMAIL_BODY_TEXT = """\
Hi {name},

I'm reaching out because DIY Realty™ is transitioning our model and we are looking for a reliable partner broker in {state} to handle our Flat Fee MLS listings. 

We pay a standard upfront fee of $150 for every MLS entry you process for our clients. This is a risk-free way to add a steady stream of listings to your pipeline with zero marketing cost or effort on your end.

If you are open to discussing this, I would love to get on a brief call to see if we'd be a good fit. 

You can book a quick chat at a time that works best for you here: https://calendar.app.google/JmdT2Xqs2nM17zw99
"""

def get_email_body_html(to_name, state):
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
    <p style="margin-bottom: 20px;">Hi {to_name},</p>

    <p style="margin-bottom: 20px;">I'm reaching out because DIY Realty&trade; is transitioning our model and we are looking for a reliable partner broker in <strong>{state}</strong> to handle our Flat Fee MLS listings.</p>

    <p style="margin-bottom: 20px;">We pay a standard upfront fee of <strong>$150 for every MLS entry</strong> you process for our clients. This is a risk-free way to add a steady stream of listings to your pipeline with zero marketing cost or effort on your end.</p>

    <p style="margin-bottom: 20px;">If you are open to discussing this, I would love to get on a brief call to see if we'd be a good fit.</p>

    <p style="margin-bottom: 40px;">You can <strong><a href="https://calendar.app.google/JmdT2Xqs2nM17zw99" class="blue-link">click here to book a quick chat</a></strong> at a time that works best for you.</p>
  </div>

  <div class="sig-text">
    <p style="margin: 0; margin-bottom: 25px;">Best Regards,</p>
    
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

</body>
</html>
"""

def build_message(to_name, to_email, location_state, from_user):
    first_name = to_name.split()[0]
    subject = EMAIL_SUBJECT.format(state=location_state)
    body_text = EMAIL_BODY_TEXT.format(name=first_name, state=location_state)
    body_html = get_email_body_html(first_name, location_state)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Vicky Thakkar <{from_user}>"
    msg["To"] = to_email
    
    msg.attach(MIMEText(body_text, "plain"))
    msg.attach(MIMEText(body_html, "html"))
    return msg

def send_test_emails():
    sender_email = "vicky@diyflatfee.com"
    sender_password = "rcdyshwonoijtppo"  # from warmup_accounts.csv
    
    test_contacts = [
        {"name": "Vicky", "email": "vicky@diyflatfee.com", "state": "AL"},
        {"name": "Darrell", "email": "dlewis@diyflatfee.com", "state": "IL"}
    ]
    
    print("Sending test emails...")
    smtp_host = "smtp.gmail.com"
    smtp_port = 465
    
    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(sender_email, sender_password)
            
            for contact in test_contacts:
                msg = build_message(
                    to_name=contact["name"], 
                    to_email=contact["email"], 
                    location_state=contact["state"],
                    from_user=sender_email
                )
                server.send_message(msg)
                print(f"OK: Sent to {contact['email']}")
                
        print("Success! Test emails sent.")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    send_test_emails()
