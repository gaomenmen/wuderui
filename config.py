import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
os.makedirs(INSTANCE_DIR, exist_ok=True)

DEFAULT_SQLITE_PATH = os.path.join(INSTANCE_DIR, 'wuderui.db')


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'wuderui-dev-secret-key-2024')
    # IMPORTANT: SQLite path is anchored to <project>/instance/ so the DB file
    # survives container/image rebuilds when that directory is mounted as a
    # persistent volume. Override with DATABASE_URL for PostgreSQL in production.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{DEFAULT_SQLITE_PATH}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_SUPPORTED_LOCALES = ['en', 'zh']
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(BASE_DIR, 'translations')
    WTF_CSRF_ENABLED = True

    # ── PayPal ──
    PAYPAL_MODE = os.environ.get('PAYPAL_MODE', 'sandbox')  # 'sandbox' or 'live'
    PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', '')
    PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET', '')
    PAYPAL_CURRENCY = os.environ.get('PAYPAL_CURRENCY', 'USD')

    # ── Analytics ──
    GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', '')
    MICROSOFT_CLARITY_ID = os.environ.get('MICROSOFT_CLARITY_ID', '')

    # ── Site metadata (SEO) ──
    SITE_URL = os.environ.get('SITE_URL', 'https://wuderui.com')
    SITE_NAME = os.environ.get('SITE_NAME', 'WuDeRuiBo')
