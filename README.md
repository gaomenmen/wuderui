# WuDeRuiBo 吴德瑞博

Chinese cultural exchange platform — Learn Mandarin, practice Tai Chi, explore China on bespoke cultural journeys.

> 中文版: [README_zh.md](README_zh.md)

## Tech Stack

- **Backend**: Flask (application factory pattern)
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: Flask-SQLAlchemy
- **Migrations**: Flask-Migrate (Alembic)
- **Auth**: Flask-Login (single admin account)
- **i18n**: Flask-Babel (EN/ZH bilingual toggle)
- **Frontend**: Bootstrap 5, Jinja2 templates, inline SVG
- **Testing**: pytest
- **Deployment**: Gunicorn + any PaaS (Render, Railway, Fly.io, etc.)

## Project Structure

```
wuderui/
├── app.py                  # Application factory + CLI commands
├── config.py               # Config class (env-based)
├── extensions.py           # db, login_manager, babel, migrate
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

## Quick Start

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
pip install pytest  # for running tests
flask run
```

Open http://127.0.0.1:5000

Default admin: `admin` / `changeme123` (you will be prompted to change it on first login)

## Local Verification

### Run the app

```bash
flask run
```

First run will auto-create SQLite database (`instance/wuderui.db`) and all tables, plus a default admin user.

### Verify pages

| Page | URL | What to check |
|------|-----|---------------|
| Homepage | `/` | Hero, 3 service cards, destination grid, testimonials |
| Learn Chinese | `/learn-chinese` | Course categories, pricing tiers, teacher cards |
| Tai Chi | `/tai-chi` | 24-form grid, pricing, benefits |
| Custom Trips | `/custom-trips` | 10 trip cards with prices, service detail panels |
| About | `/about` | Story, philosophy |
| Contact | `/contact` | Contact methods with links, inquiry form |
| Affiliate | `/affiliate` | Referral program info |
| Admin Login | `/admin/login` | Login with `admin` / `changeme123` |

### Verify admin panel

1. Login at `/admin/login` with `admin` / `changeme123`
2. **Dashboard** — check stats display
3. **Content** → click "Sync All Defaults" → verify 27 sections created across 7 pages
4. Edit a section title → visit the public page → confirm updated text appears
5. Delete a section → public page reverts to default
6. **Affiliates** → create one → verify referral code generated
7. Visit `/?ref=WDR-XXXX` → check referral click logged in admin
8. Submit contact form → inquiry appears in admin panel
9. Convert inquiry → create commission → mark as paid

### Verify new features

#### CMS Content Management

1. Login to admin → **Content** → click "Sync All Defaults"
2. Select a page (e.g. Homepage) → edit a section's English/Chinese title
3. Visit the public page → confirm the updated text appears
4. Toggle a section invisible → public page shows the hardcoded fallback
5. Delete a section → public page fully reverts to default
6. Drag-and-drop to reorder sections → public page reflects new order

#### Custom Trips — Clickable Service Panels

1. Visit `/custom-trips`
2. Scroll to the 4 service cards: Photography, Local Food, English Guide, 24/7 Support
3. Click each card — panel expands with detailed content, previous panel auto-collapses
4. Active card shows highlighted border and lift animation
5. The Local Food panel lists dishes from the same 10 destinations as the trip cards

#### Service Pricing

All three service pages now include pricing:

- **Learn Chinese** (`/learn-chinese`): 3 tiers — Free / ¥1,680 Standard / ¥4,200 Intensive
- **Tai Chi** (`/tai-chi`): 3 tiers — Free / $49 Full Course / $129 Private Coaching
- **Custom Trips** (`/custom-trips`): 10 destinations, ¥4,800–¥12,800 per person

### Create additional admin

```bash
flask create-admin <username> <password>
```

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

15 tests cover: model logic (password hashing, commission rates, CMS sections), route handling (contact form, referral tracking, admin auth), and admin CRUD operations.

## Database Migrations

Schema changes are managed with Flask-Migrate:

```bash
flask db migrate -m "description of change"  # generate migration
flask db upgrade                               # apply migration
```

For development, `db.create_all()` runs automatically on startup. For production, use `flask db upgrade` to apply migrations safely.

## Production Security Checklist

Before deploying to production:

- [ ] Set `SECRET_KEY` to a strong random string (32+ chars)
- [ ] Set `DATABASE_URL` to a PostgreSQL connection string
- [ ] Change default admin password (first login forces password change)
- [ ] Set `ADMIN_PASSWORD` env var for initial admin password
- [ ] Ensure `FLASK_DEBUG` is not enabled
- [ ] Use HTTPS (most PaaS platforms handle this automatically)
- [ ] Review contact information in templates — replace demo data with real info

## Admin Panel Guide

Login at `/admin/login`

### Content Management (CMS)

Manage page content without editing code.

1. **Content** → click "Sync All Defaults" to import existing content
2. Select a page → edit section titles, body text, images, buttons
3. Toggle sections visible/hidden, reorder via drag-and-drop
4. Delete a section to revert to hardcoded default

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

## Deployment

The app is ready for deployment with Gunicorn:

```bash
gunicorn app:app
```

Set environment variables on your hosting platform:

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Random 32+ char string for session encryption |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `ADMIN_PASSWORD` | No | Initial admin password (default: `changeme123`) |

See [.env.example](.env.example) for a full configuration template.

Compatible with any Python-friendly PaaS (Render, Railway, Fly.io, Heroku, etc.).

### Media File Storage

CMS image URLs point to external hosts. The app does not currently handle file uploads. If you add image upload in the future, use cloud storage (S3, Cloudflare R2, etc.) — PaaS filesystems are ephemeral and will lose uploaded files on restart.

## Test Contact Info (Demo)

| Channel | Value |
|---------|-------|
| WhatsApp | +86 138-0013-8000 |
| WeChat ID | WuDeRuiBo2026 |
| Facebook | facebook.com/wuderuibo |
| Email | hello@wuderuibo.com |

These are demo/test values. Replace with real contact info before going live.
