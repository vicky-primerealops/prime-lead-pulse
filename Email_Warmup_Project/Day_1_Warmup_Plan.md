# Day 1: Email Warmup Action Plan

This is a critical phase. If we rush this, the accounts will be burned. We are going to simulate human behavior by sending plain-text, casual emails between your own 13 accounts.

## Step 1: Account Preparation (Manual)
For **every single one** of the 13 Gmail accounts, you need to do the following:

1. **Rename the Account (Optional):** Go to `myaccount.google.com` > **Personal Info** > **Email** and change the name if the option is available.
2. **Setup Auto-Forwarding:**
   * Go to Gmail **Settings (Gear Icon)** > **See all settings** > **Forwarding and POP/IMAP**.
   * Click **Add a forwarding address** and enter `info@primerealops.com`.
   * Follow the verification link sent to `info@primerealops.com`.
   * Make sure you select **"Forward a copy of incoming mail to..."** and save changes.
3. **Generate an App Password:**
   * Go to `myaccount.google.com/security`.
   * Ensure **2-Step Verification** is turned ON.
   * Search for **App Passwords** in the search bar.
   * Create an app password named `Warmup Script`. 
   * **Copy the 16-character password and save it in a safe place.**

## Step 2: Create the Data File
I have written a Python script in your project folder called `warmup.py`. For it to work, you need to create a simple Excel/CSV file.

1. In your `PROps Things` folder, create a file named exactly: `warmup_accounts.csv`.
2. It must have exactly these two column headers in the first row: `Email` and `AppPassword`.
3. List all 13 accounts and their 16-character App Passwords. (Remove spaces from the passwords).

*Example:*
```csv
Email,AppPassword
vickythakkar6143@gmail.com,abcdefghijklmnop
vickythegeneralist@gmail.com,qrstuvwxyzabcdef
... (all 13 accounts)
```

## Step 3: Run the Script Daily for Week 1
Once the CSV is ready, open your terminal (PowerShell) and run:
```bash
cd "C:\Users\vicky\Desktop\Technical Things\PROps Things"
python warmup.py
```

### What the script does:
* It reads your 13 accounts.
* It logs into Account A.
* It randomly selects 5 to 8 *other* accounts from your list. (This perfectly aligns with your PDF's Week 1 goal of 5-10 emails/day).
* It sends a highly varied, plain-text email with random subjects like "Checking in" or "Meeting notes" to simulate real human conversation.
* It waits randomly between 30-90 seconds between emails to look like a human typing.
* It repeats this for all 13 accounts.

### Your Daily Task:
* Run this script **once a day** for the next 5-7 days. 
* **Crucial:** Log into `info@primerealops.com` periodically. Since you forwarded everything there, you will see these warmup emails arrive. If any land in Spam, **you must click "Report Not Spam"**. This trains Google's filters.

Let me know when you have completed Steps 1 and 2, and if you have any questions!
