# 🚀 GitHub Actions Setup Guide
### Auto-send 50 emails daily at 7:30 PM IST — no laptop needed

---

## What you need
- A free [GitHub account](https://github.com) (create one if you don't have it)
- Git installed on your laptop (one-time setup, only for the upload)
- ~10 minutes

---

## Step 1 — Install Git (if not already installed)

1. Go to https://git-scm.com/download/win
2. Download and install (all defaults are fine)
3. Open **PowerShell** or **Command Prompt** and confirm it works:
   ```
   git --version
   ```

---

## Step 2 — Create a Private GitHub Repository

1. Go to [github.com](https://github.com) → click **"New"** (green button, top left)
2. Fill in:
   - **Repository name:** `primeralops-emailer` (or anything you like)
   - **Visibility:** ✅ **Private** ← very important!
   - Leave everything else as default
3. Click **"Create repository"**

---

## Step 3 — Add GitHub Secrets (your passwords go here, NOT in code)

In your new repo, go to:
**Settings → Secrets and variables → Actions → New repository secret**

Add each of these secrets one by one:

| Secret Name | Value |
|---|---|
| `SPREADSHEET_ID` | `1GAecP1KrbM_ehj8RjUN9cuEpk0lB7l-1-t_TikAShOs` |
| `SMTP_HOST` | `smtpout.secureserver.net` |
| `SMTP_PORT` | `465` |
| `SMTP_USER` | `info@primerealops.com` |
| `SMTP_PASSWORD` | `SZCbs.VBJKbE=Q9` |
| `FROM_NAME` | `Prime Real Ops` |
| `SERVICE_ACCOUNT_JSON` | *(see below)* |

### For `SERVICE_ACCOUNT_JSON`:
1. Open `service_account.json` from your project folder in Notepad
2. Select ALL the text (Ctrl+A) → Copy (Ctrl+C)
3. Paste the entire JSON content as the secret value

---

## Step 4 — Upload Your Code to GitHub

Open **PowerShell**, navigate to your project folder, and run these commands **one by one**:

```powershell
cd "C:\Users\vicky\Desktop\Technical Things\PROps Things"

git init
git add send_emails.py requirements.txt .gitignore .github
git commit -m "Initial commit: email automation with GitHub Actions"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/primeralops-emailer.git
git push -u origin main
```

> ⚠️ Replace `YOUR_USERNAME` with your actual GitHub username!

> ✅ Notice `config.py` and `service_account.json` are **NOT** in the `git add` command — they stay local and private.

---

## Step 5 — Verify It Worked

1. Go to your GitHub repo → click the **"Actions"** tab
2. You should see the workflow **"Send Daily Outreach Emails"** listed
3. It will run automatically every day at **7:30 PM IST**

### 🧪 Test it right now (optional)
1. In the **Actions** tab → click **"Send Daily Outreach Emails"**
2. Click **"Run workflow"** → **"Run workflow"** (green button)
3. Watch the logs in real time!

---

## How it works (summary)

```
Every day at 7:30 PM IST
        ↓
GitHub's cloud server wakes up
        ↓
Installs Python + dependencies
        ↓
Reads secrets → builds config.py + service_account.json
        ↓
Runs: python send_emails.py --auto
        ↓
Sends up to 50 unsent emails from your Sheet
        ↓
Stamps each row with date+time in column C
        ↓
Saves copy to your GoDaddy Sent folder
        ↓
Server shuts down (you pay nothing)
```

---

## ❓ FAQ

**Q: What if there are no unsent contacts left?**  
A: The script logs "No unsent contacts found. Nothing to do." and exits cleanly. No error, no emails sent.

**Q: Can I trigger it manually anytime?**  
A: Yes! Go to Actions tab → "Send Daily Outreach Emails" → "Run workflow".

**Q: How do I see if it succeeded?**  
A: Actions tab shows a ✅ green tick for success, ❌ red X for failure. You can click to see full logs.

**Q: GitHub says the schedule is approximate — why?**  
A: GitHub Actions cron jobs can be delayed by up to 15–30 min during high traffic. 7:30 PM IST could run at 7:35–8:00 PM occasionally. This is normal and fine.

**Q: What if I want to change the email content or timing later?**  
A: Edit `.github/workflows/send_emails.yml` (change `cron: "0 14 * * *"`) or `send_emails.py` on GitHub directly, or push changes from your laptop.
