# 📧 Your Automated Email Setup — Step by Step
### Written for non-technical users. Follow exactly as written.

---

## 🧭 OVERVIEW
You'll do this **once**. After that, emails go out every day at 7:30 PM by themselves.

**Total time:** ~15 minutes  
**What you need:** Your laptop, an internet connection, and this guide open.

---

---

# PART 1 — Install Git
### (Git is a free tool that lets you upload code to the internet)

---

### Step 1 — Download Git

1. Open your browser (Chrome, Edge, etc.)
2. Go to this link: **https://git-scm.com/download/win**
3. The download should start automatically. If not, click **"Click here to download"**
4. You'll get a file like `Git-2.xx.x-64-bit.exe` in your Downloads folder

---

### Step 2 — Install Git

1. Open your **Downloads** folder
2. Double-click the file you just downloaded (`Git-2.xx.x-64-bit.exe`)
3. If Windows asks *"Do you want to allow this app to make changes?"* → click **Yes**
4. Click **Next** on every screen (all the default options are fine)
5. At the very end, click **Install**, then **Finish**

---

### Step 3 — Confirm Git is installed

1. Press the **Windows key** on your keyboard (the ⊞ key between Ctrl and Alt)
2. Type: `powershell`
3. Click on **Windows PowerShell** (the blue icon)
4. A black/dark blue window will open — this is PowerShell
5. Type this exactly and press Enter:
   ```
   git --version
   ```
6. You should see something like `git version 2.45.0` — that means it worked! ✅

> 💡 **Keep this PowerShell window open** — you'll need it later in Part 4.

---

---

# PART 2 — Create a Free GitHub Account
### (GitHub is the cloud where your script will live and run)

---

### Step 4 — Sign up for GitHub

1. Open your browser
2. Go to: **https://github.com**
3. Click the **"Sign up"** button (top right corner)
4. Enter:
   - Your email address
   - Create a password
   - Choose a username (e.g. `vickyprimeops`)
5. Complete the puzzle/verification if it shows one
6. Check your email and click the verification link GitHub sends you
7. When it asks about your plan → choose **"Free"** (the free plan is perfect for this)

> ✅ You now have a GitHub account. Remember your username and password.

---

---

# PART 3 — Create Your Private Repository
### (A "repository" is just a folder on GitHub where your files live)

---

### Step 5 — Create the repository

1. Go to: **https://github.com** and make sure you're logged in
2. Look at the **top left area** — you'll see a green button that says **"New"**
   - If you don't see it, click the **cat logo** (GitHub's logo) at the very top left, then look for a green **"New"** button
3. Click the **"New"** button
4. You'll see a form. Fill it in like this:
   - **Repository name:** Type `primeops-emailer`
   - **Description:** (optional) Type `Daily email automation`
   - Click the **"Private"** radio button ← **IMPORTANT!** This keeps your repo hidden from others
   - Leave everything else as-is (don't tick any checkboxes at the bottom)
5. Scroll down and click the big green **"Create repository"** button

> ✅ Your repository is created. You'll see a page with some code on it — that's normal, ignore it for now.

---

---

# PART 4 — Add Your Secrets
### (Secrets are where your passwords are stored safely — encrypted by GitHub)

---

### Step 6 — Open the Secrets settings

1. You should be on your new repository page (it'll say `YOUR_USERNAME/primeops-emailer` at the top)
2. Look at the row of tabs near the top: **Code, Issues, Pull requests, Actions, Projects, Security, Insights, Settings**
3. Click **"Settings"** (the last tab on the right)
4. On the LEFT sidebar, scroll down until you see **"Secrets and variables"** — click on it
5. It will expand — click **"Actions"** underneath it
6. You'll see a page that says **"Actions secrets and variables"**
7. Click the green **"New repository secret"** button

---

### Step 7 — Add the secrets one by one

You need to add **7 secrets**. For each one:
- Click **"New repository secret"**  
- Type the **Name** exactly as shown  
- Paste or type the **Value** exactly as shown  
- Click the green **"Add secret"** button  

Here are all 7:

---

**Secret 1:**
- **Name:** `SPREADSHEET_ID`
- **Value:** `1GAecP1KrbM_ehj8RjUN9cuEpk0lB7l-1-t_TikAShOs`
- Click **Add secret**

---

**Secret 2:**
- **Name:** `SMTP_HOST`
- **Value:** `smtpout.secureserver.net`
- Click **Add secret**

---

**Secret 3:**
- **Name:** `SMTP_PORT`
- **Value:** `465`
- Click **Add secret**

---

**Secret 4:**
- **Name:** `SMTP_USER`
- **Value:** `info@primerealops.com`
- Click **Add secret**

---

**Secret 5:**
- **Name:** `SMTP_PASSWORD`
- **Value:** `SZCbs.VBJKbE=Q9`
- Click **Add secret**

---

**Secret 6:**
- **Name:** `FROM_NAME`
- **Value:** `Prime Real Ops`
- Click **Add secret**

---

**Secret 7 (the big one — your Google service account):**
- **Name:** `SERVICE_ACCOUNT_JSON`
- **Value:** Follow these steps to get it:
  1. Open **File Explorer** (the folder icon on your taskbar)
  2. Navigate to: `C:\Users\vicky\Desktop\Technical Things\PROps Things`
  3. You'll see a file called `service_account.json`
  4. Right-click on it → click **"Open with"** → click **"Notepad"**
  5. Press **Ctrl+A** (to select all the text)
  6. Press **Ctrl+C** (to copy it)
  7. Go back to GitHub, click in the **"Secret"** box, press **Ctrl+V** to paste
- Click **Add secret**

> ✅ You should now see all 7 secrets listed on that page. 

---

---

# PART 5 — Upload Your Code to GitHub
### (This is a one-time upload from your laptop to GitHub)

---

### Step 8 — Go back to your PowerShell window

Remember the PowerShell window from Step 3? Go back to it.

If you closed it:
1. Press **Windows key** → type `powershell` → press Enter

---

### Step 9 — Run these commands

Copy and paste each line below into PowerShell **one at a time**, pressing **Enter** after each one.

**Command 1** — Go to your project folder:
```
cd "C:\Users\vicky\Desktop\Technical Things\PROps Things"
```

**Command 2** — Set up Git in the folder:
```
git init
```

**Command 3** — Tell Git who you are (replace with your real name and email):
```
git config user.email "you@youremail.com"
```
```
git config user.name "Vicky Thakkar"
```

**Command 4** — Select the files to upload (this does NOT include your passwords):
```
git add send_emails.py requirements.txt .gitignore .github
```

**Command 5** — Save a snapshot:
```
git commit -m "Initial commit: email automation"
```

**Command 6** — Set the main branch:
```
git branch -M main
```

**Command 7** — Connect to your GitHub repo.
⚠️ **Replace `YOUR_USERNAME`** with your actual GitHub username before pasting:
```
git remote add origin https://github.com/YOUR_USERNAME/primeops-emailer.git
```

**Command 8** — Upload the files:
```
git push -u origin main
```

---

### Step 10 — GitHub will ask you to log in

When you run Command 8, a window will pop up asking you to sign in to GitHub.
- Click **"Sign in with your browser"**
- It will open GitHub in your browser — click **"Authorize"**
- Come back to PowerShell — you'll see it uploading

> ✅ If you see `Branch 'main' set up to track remote branch 'main'` — the upload worked!

---

---

# PART 6 — Test It & Confirm It's Working

---

### Step 11 — Check your files are on GitHub

1. Go to **https://github.com/YOUR_USERNAME/primeops-emailer** (replace YOUR_USERNAME)
2. You should see 3 files listed:
   - `send_emails.py`
   - `requirements.txt`
   - `.gitignore`
   - And a `.github` folder
3. ✅ If you see them — your code is live on GitHub!

---

### Step 12 — Test the automation manually RIGHT NOW

You don't have to wait until 7:30 PM. Let's trigger it manually to make sure it works.

1. On your GitHub repo page, click the **"Actions"** tab (in the top row of tabs)
2. On the left side, you'll see **"Send Daily Outreach Emails"** — click on it
3. On the right side, you'll see a button that says **"Run workflow"** — click it
4. A small box will appear — click the green **"Run workflow"** button inside it
5. You'll see a yellow circle ⏳ appear — that means it's running!
6. Wait ~2 minutes, then refresh the page
7. If it turns into a ✅ green checkmark — **it worked! Emails were sent!**
8. If it turns into a ❌ red X — click on it to see what went wrong, and share the error with me

---

### Step 13 — Check your Google Sheet

After the test run, open your Google Sheet. You should see timestamps in **Column C** for the rows that were just emailed. That confirms the emails went out!

---

---

# 🎉 YOU'RE DONE!

From this point on, every day at **7:30 PM IST**:
- GitHub's server wakes up automatically
- Sends 50 emails from your sheet
- Stamps the sheet with timestamps
- Saves copies to your GoDaddy Sent folder
- Goes back to sleep

**Your laptop can be completely off. Nothing needed from you.**

---

## 📌 Quick Reference — Things to Remember

| What | Where |
|---|---|
| See if today's emails were sent | GitHub → Actions tab → latest run → ✅ or ❌ |
| Trigger emails manually anytime | GitHub → Actions → "Run workflow" |
| Check which emails were sent | Google Sheet → Column C (has timestamps) |
| Change the time (7:30 PM) | Ask me and I'll update it for you |

---

## 🆘 If Something Goes Wrong

Just share the error message with me and I'll fix it immediately.
Common things that can go wrong and are easy to fix:
- Wrong secret value → just go back to Settings → Secrets and edit it
- Typo in a command → just run the command again
