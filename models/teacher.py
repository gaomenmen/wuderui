from extensions import db
from datetime import datetime, timezone


class Teacher(db.Model):
    __tablename__ = 'teacher'

    id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(120), nullable=False)
    name_zh = db.Column(db.String(120))
    photo_url = db.Column(db.String(500))
    bio_en = db.Column(db.Text)
    bio_zh = db.Column(db.Text)
    experience_en = db.Column(db.Text)
    experience_zh = db.Column(db.Text)
    specialty_en = db.Column(db.String(200))
    specialty_zh = db.Column(db.String(200))
    languages = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
