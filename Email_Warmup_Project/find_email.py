import imaplib
import csv
import email as emaillib

with open('C:/Users/vicky/Desktop/Technical Things/PROps Things/Email_Warmup_Project/warmup_accounts.csv') as f:
    accounts = list(csv.DictReader(f))

target_acc = next(a for a in accounts if a['Email'].lower() == 'vicky@diyflatfee.com')
mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(target_acc['Email'], target_acc['AppPassword'])

status, folder_list = mail.list()
folders = []
for entry in folder_list:
    decoded = entry.decode() if isinstance(entry, bytes) else entry
    parts = decoded.split('"/"')
    if len(parts) >= 2:
        folders.append(parts[-1].strip().strip('"'))

found_locations = []
for folder in folders:
    try:
        mail.select(f'"{folder}"', readonly=True)
        status, messages = mail.search(None, '(SUBJECT "3015 Brownsboro Rd Apt 1")')
        if status == 'OK' and messages[0]:
            found_locations.append((folder, len(messages[0].split())))
            if folder == '[Gmail]/Trash':
                nums = messages[0].split()
                for num in nums:
                    typ, data = mail.fetch(num, '(BODY[HEADER.FIELDS (FROM TO CC)])')
                    print(f"TRASH {num}: {data[0][1]}")
    except:
        pass

print('Found in:', found_locations)
