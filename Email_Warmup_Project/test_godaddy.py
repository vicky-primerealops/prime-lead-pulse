import imaplib
import csv
import email as emaillib

with open('C:/Users/vicky/Desktop/Technical Things/PROps Things/Email_Warmup_Project/warmup_accounts.csv') as f:
    accounts = list(csv.DictReader(f))

target_acc = next(a for a in accounts if a['Email'].lower() == 'info@primerealops.com')
mail = imaplib.IMAP4_SSL('imap.secureserver.net')
mail.login(target_acc['Email'], target_acc['AppPassword'])
mail.select('INBOX', readonly=False)

status, messages = mail.search(None, 'ALL')
if messages[0]:
    nums = messages[0].split()
    print("Total ALL nums:", len(nums))
    test_nums = b','.join(nums[:50])
    print("Testing fetch with", len(nums[:50]), "nums")
    try:
        typ, data = mail.store(test_nums, "+FLAGS", "\\Deleted")
        print("Store result:", typ)
    except Exception as e:
        print("Store error:", e)
