import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'wuderui-dev-secret-key-2024')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///wuderui.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_SUPPORTED_LOCALES = ['en', 'zh']
    WTF_CSRF_ENABLED = True
