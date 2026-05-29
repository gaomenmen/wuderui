from extensions import db
from datetime import datetime, timezone


class ChineseCourse(db.Model):
    __tablename__ = 'chinese_course'

    CATEGORIES = ['kids', 'adult', 'pinyin', 'sentence', 'conversation', 'business']

    id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(200), nullable=False)
    name_zh = db.Column(db.String(200))
    category = db.Column(db.String(40), nullable=False, default='adult')
    description_en = db.Column(db.Text)
    description_zh = db.Column(db.Text)
    sample_video_url = db.Column(db.String(500))
    cover_image = db.Column(db.String(500))
    price = db.Column(db.Float)
    currency = db.Column(db.String(10), default='USD')
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
