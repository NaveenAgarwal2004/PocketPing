# Expense Bot — Setup Guide

A Telegram bot that logs your expenses to Google Sheets in plain text.
Send `lunch 80 cash` → it saves Date, Description, Category, Amount, Account automatically.

---

## What you need

- A Telegram account (already have it)
- A Google account (already have it)
- A free cloud server to keep the bot running 24/7
  → Recommended: **Railway.app** (free tier, no credit card needed)
  → Alternatively: any PC/laptop you leave on, or a cheap VPS

---

## Step 1 — Create the Telegram Bot (5 min)

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name: `Naveen Expense Bot`
4. Choose a username: `naveen_expense_bot` (must end in `bot`)
5. BotFather gives you a **token** like:
   ```
   7412345678:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
6. Copy and save this token — this is your `TELEGRAM_BOT_TOKEN`

---

## Step 2 — Find your Telegram User ID (2 min)

1. In Telegram, search for **@userinfobot**
2. Send `/start`
3. It replies with your **Id** number (e.g. `812345678`)
4. Save this — this is your `ALLOWED_USER_IDS`

This ensures only you can use the bot.

---

## Step 3 — Create Google Sheet + Service Account (10 min)

### 3a. Create the Sheet
1. Go to [sheets.google.com](https://sheets.google.com)
2. Create a new sheet → name it **"My Expenses 2026"** (or anything)
3. Copy the Sheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/THIS_PART_IS_THE_ID/edit
   ```
4. Save this — this is your `GOOGLE_SHEET_ID`

### 3b. Create a Service Account
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (e.g. `expense-bot`)
3. Go to **APIs & Services → Enable APIs**
   - Enable: **Google Sheets API**
   - Enable: **Google Drive API**
4. Go to **APIs & Services → Credentials**
5. Click **Create Credentials → Service Account**
   - Name: `expense-bot`
   - Click through to finish
6. Click on the new service account → **Keys tab → Add Key → JSON**
7. A file `credentials.json` downloads — keep it safe, never share it publicly

### 3c. Share the Sheet with the Service Account
1. Open `credentials.json` in Notepad
2. Find `"client_email"` — looks like `expense-bot@your-project.iam.gserviceaccount.com`
3. Open your Google Sheet
4. Click **Share** (top right)
5. Paste that email → set role to **Editor** → Share

---

## Step 4 — Deploy on Railway (free, 5 min)

Railway lets you run the bot 24/7 for free without keeping your laptop on.

1. Go to [railway.app](https://railway.app) → Sign up with GitHub
2. Click **New Project → Deploy from GitHub repo**
   - Push your bot files to a GitHub repo first (just drag-and-drop on github.com)
   - Select that repo
3. Go to your service → **Variables tab** → add these:
   ```
   TELEGRAM_BOT_TOKEN   = your bot token
   GOOGLE_SHEET_ID      = your sheet id
   ALLOWED_USER_IDS     = your telegram user id
   ```
4. Upload `credentials.json`:
   - Go to **Files** tab in Railway
   - Upload `credentials.json` to the root
   - Set `GOOGLE_CREDS_FILE = credentials.json`
5. Railway auto-deploys. Bot is live!

---

## Step 5 — Test it

Open your bot on Telegram and send:

```
lunch 80 cash
```

You should get back:
```
✓ Logged!
  23-06-2026  |  Lunch
  Food  ·  ₹80  ·  Cash
```

Check your Google Sheet — a new row appears instantly.

---

## How to send expenses (quick reference)

| What you type | What gets logged |
|---|---|
| `chai 20 cash` | Food · Chai · ₹20 · Cash |
| `uber 137 bob` | Transport · Uber · ₹137 · BOB |
| `metro 25 indusind` | Metro · Metro · ₹25 · IndusInd |
| `medicine 250 upi` | Health · Medicine · ₹250 · UPI |
| `light bill 636 bob` | Bills · Light Bill · ₹636 · BOB |
| `repair 500 cash` | Home · Repair · ₹500 · Cash |
| `/today` | Shows today's total |

**No account mentioned = Cash by default**
So you can just type `chai 20` for quick cash entries.

---

## Auto-detected categories

| Category | Triggered by keywords |
|---|---|
| Transport | uber, ola, auto, rapido, taxi, bike |
| Metro | metro, dmrc, card recharge |
| Food | lunch, dinner, chai, juice, zomato, swiggy |
| Bills | bill, electricity, water, internet, recharge |
| Home | repair, plumber, carpenter, rent |
| Entertainment | movie, cinema, netflix, pvr |
| Shopping | amazon, clothes, grocery, kirana |
| Health | medicine, doctor, pharmacy, chemist |

---

## Local setup (optional, if you want to run on your own PC)

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and fill the env file
cp .env.example .env
# Edit .env with your tokens

# Run
source .env
python bot.py
```

To keep it running even when your terminal closes:
```bash
nohup python bot.py &
```

---

## Sync data to this Claude tracker

Whenever you want to review or analyse expenses here, just paste:
> "Log these from my sheet: [paste rows]"

Or ask: "How much did I spend on food this month?" and paste the data.
