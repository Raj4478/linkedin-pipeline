<div align="center">

# 💼 LinkedIn Pipeline

### Automated LinkedIn content for Indian software engineers

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com)
[![Gemini](https://img.shields.io/badge/Gemini_AI-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/features/actions)

**Posts 3x/day automatically** — system design, backend tips, and career advice tailored for Indian developers.

</div>

---

## 🏗️ Architecture

```
GitHub Actions (cron 3x/day)
        │
        ▼
  TopicBank.pick_unused()     ← rotates topics, no repeats
        │
        ▼
  PostGenerator (Gemini AI)   ← generates LinkedIn-optimized post
        │
        ▼
  LinkedInPublisher           ← posts via LinkedIn API v2 (OAuth2)
        │
        ▼
  Telegram notification       ← confirms post with URL
        │
        ▼
  Topic tracker commit        ← saves used topics to repo
```

---

## ✨ Features

- **3 niches** — System Design, Backend/WebDev, Career Advice
- **Indian context** — Zomato, Swiggy, Razorpay, PhonePe examples
- **No repeats** — topic tracker persists across runs
- **Completely free** — LinkedIn API has no posting limits
- **Auto-rotation** — 9AM system design, 1PM webdev, 6PM career
- **Telegram alerts** — get notified on every post or failure

---

## 🚀 Setup

### Step 1 — LinkedIn Developer App

1. Go to [linkedin.com/developers](https://www.linkedin.com/developers/apps)
2. Create a new app
3. Add products: **Sign In with LinkedIn** + **Share on LinkedIn**
4. Set redirect URI: `http://localhost:8888/callback`
5. Copy your **Client ID** and **Client Secret**

### Step 2 — Get Access Token (one-time, run locally)

```bash
pip install httpx
LINKEDIN_CLIENT_ID=xxx LINKEDIN_CLIENT_SECRET=yyy python get_linkedin_token.py
```

This opens your browser, you log in once, and it prints:
```
LINKEDIN_ACCESS_TOKEN=AQV8...
LINKEDIN_PERSON_URN=urn:li:person:XXXXXXX
```

Token is valid for **~60 days**. Re-run when it expires.

### Step 3 — GitHub Secrets

Go to repo → Settings → Secrets → Actions → add:

| Secret | Value |
|---|---|
| `GEMINI_API_KEY` | From [ai.google.dev](https://ai.google.dev) |
| `LINKEDIN_ACCESS_TOKEN` | From step 2 |
| `LINKEDIN_PERSON_URN` | From step 2 |
| `TELEGRAM_BOT_TOKEN` | Optional |
| `TELEGRAM_ALLOWED_USER_ID` | Optional |

### Step 4 — Run it

Push to main → GitHub Actions runs automatically 3x/day.

Manual trigger: Actions tab → Daily LinkedIn Dev Content → Run workflow.

---

## 🧪 Local Testing

```bash
pip install -r requirements.txt
cp .env.example .env  # fill in your values

# Dry run (no actual posting)
python -m src.pipeline --niche system_design --dry-run

# Post for real
python -m src.pipeline --niche webdev --topic "NestJS dependency injection"

# Specific niche
python -m src.pipeline --niche career
```

---

## 📁 Structure

```
linkedin-pipeline/
├── src/
│   ├── generators/
│   │   └── post_generator.py    # Gemini AI post generation
│   └── publishers/
│       └── linkedin_publisher.py # LinkedIn API v2 OAuth2
├── config/
│   ├── settings.py              # Pydantic settings
│   └── topics.py                # Topic bank + rotation
├── .github/workflows/
│   └── daily_post.yml           # Cron: 3x/day
├── get_linkedin_token.py        # One-time auth helper
└── requirements.txt
```

---

## 👤 Author

**Rajeshwar Singh** — SDE-I @ Bimaplan (YC-backed)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/rajeshwar-singh-b6990419a)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat&logo=github&logoColor=white)](https://github.com/Raj4478)
