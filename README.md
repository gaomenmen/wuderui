# WuDeRuiBo 吴德瑞博

Chinese cultural exchange platform — Learn Mandarin, practice Tai Chi, explore China on bespoke cultural journeys.

> 中文版: [README_zh.md](README_zh.md)

## Tech Stack

- **Backend**: Flask (application factory pattern)
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: Flask-SQLAlchemy
- **Auth**: Flask-Login (single admin account)
- **i18n**: Flask-Babel (EN/ZH bilingual toggle)
- **Frontend**: Bootstrap 5, Jinja2 templates, inline SVG
- **Deployment**: Render.com + Gunicorn + GitHub auto-deploy

## Project Structure

```
wuderui/
├── app.py                  # Application factory + CLI commands
├── config.py               # Config class (env-based)
├── extensions.py           # db, login_manager, babel
├── requirements.txt
├── admin/
│   └── routes.py           # Admin panel routes (14+ routes)
├── models/
│   ├── admin_user.py       # Admin login
│   ├── affiliate.py        # Referral partners
│   ├── referral_click.py   # Click tracking
│   ├── inquiry.py          # Contact form submissions
│   ├── commission.py       # Commission records
│   ├── monthly_report.py   # Monthly summaries
│   └── page_section.py     # CMS content blocks
├── routes/
│   ├── main.py             # Public pages + referral cookie
│   ├── contact.py          # Contact form POST handler
│   └── auth.py             # Admin login/logout
└── templates/
    ├── base.html            # Master layout (navbar, footer, bilingual CSS)
    ├── index.html           # Homepage
    ├── learn_chinese.html   # Chinese courses
    ├── tai_chi.html         # Tai Chi 24-form
    ├── custom_trips.html    # 10 curated travel packages
    ├── about.html           # About us
    ├── contact.html         # Contact form + FAQ
    ├── affiliate.html       # Referral program
    ├── auth/login.html      # Admin login page
    └── admin/               # 14 admin panel templates
        ├── base.html        # Admin sidebar layout
        ├── content/         # CMS templates (pages, sections, section_form)
        └── ...
```

## Local Development

### Prerequisites

- Python 3.10+
- Git

### Setup

```bash
git clone https://github.com/gaomenmen/wuderui.git
cd wuderui
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
flask run
```

Open http://127.0.0.1:5000

Default admin: `admin` / `changeme123`

## Deploy to Render.com

### 1. Create Render account

Sign up at https://render.com and connect your GitHub account.

### 2. Create PostgreSQL database

- Dashboard → New → PostgreSQL
- Note the **Internal Database URL** (e.g. `postgresql://user:pass@host/db`)

### 3. Create Web Service

- Dashboard → New → Web Service
- Connect your GitHub repo
- Settings:
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `gunicorn app:app`
  - **Environment**: Python 3

### 4. Set Environment Variables

In Render Web Service → Environment:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | Random 32+ char string (e.g. `openssl rand -hex 32`) |
| `DATABASE_URL` | PostgreSQL Internal URL from step 2 |

### 5. Deploy

Render auto-deploys on every `git push` to `main`.

First deploy will:
- Create all database tables
- Create default admin user (`admin` / `changeme123`)

**Change the admin password immediately after first login.**

### 6. Create additional admin (optional)

```bash
# Using Render Shell
flask create-admin <username> <password>
```

## Admin Panel Guide

Login at `/admin/login`

### Dashboard

Overview stats: total inquiries, new inquiries, active affiliates, monthly commission total.

### Content Management (CMS)

Manage page content without editing code.

1. **Content** → Select a page (Home, Learn Chinese, Tai Chi, etc.)
2. **New Section** → Fill in bilingual fields:
   - `section_key`: identifier (e.g. `hero`, `pricing`, `cta`)
   - `section_type`: `hero`, `card`, `text_block`, `stats`, `cta`, `faq`
   - Title, subtitle, body — English and Chinese
   - Image URL, button text, button URL
   - `extra_data`: JSON for flexible content (tags, stat values)
3. Sections appear on the public page; delete a section to revert to default

All 7 public pages support CMS hero editing. Content falls back to hardcoded defaults when no CMS section exists.

### Inquiries

View all contact form submissions. Update status pipeline: New → Contacted → Converted → Closed.

### Affiliates

Manage referral partners. Each affiliate gets a unique referral code (e.g. `WDR-A3F7`).

Referral tracking flow:
1. Visitor clicks `yoursite.com/?ref=WDR-A3F7`
2. System logs the click and sets a 30-day cookie
3. Visitor submits contact form → inquiry linked to affiliate
4. Admin marks inquiry as "converted" → create commission

### Commissions

Commission rates per service type:
- Chinese courses: 5%
- Tai Chi: 8%
- Travel packages: 10%

Bulk approve and mark-as-paid supported.

### Reports & Settlements

Generate monthly per-affiliate summaries. View paid commission history.

## Bilingual System

The site supports English/Chinese toggle:

- URL parameter: `?lang=en` or `?lang=zh`
- Template pattern: `<span class="en">English</span><span class="zh">中文</span>`
- CSS hides one language based on `<html>` class

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Production | `wuderui-dev-secret-key-2024` | Flask session encryption |
| `DATABASE_URL` | Production | `sqlite:///wuderui.db` | Database connection string |

## Test Contact Info (Demo)

| Channel | Value |
|---------|-------|
| WhatsApp | +86 138-0013-8000 |
| WeChat ID | WuDeRuiBo2026 |
| Facebook | facebook.com/wuderuibo |
| Email | hello@wuderuibo.com |
