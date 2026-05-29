from extensions import db
from datetime import datetime, timezone


class TaiChiLesson(db.Model):
    __tablename__ = 'tai_chi_lesson'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False)
    name_en = db.Column(db.String(200), nullable=False)
    name_zh = db.Column(db.String(200))
    video_url = db.Column(db.String(500))
    thumbnail_url = db.Column(db.String(500))
    duration_seconds = db.Column(db.Integer)
    description_en = db.Column(db.Text)
    description_zh = db.Column(db.Text)
    key_points_en = db.Column(db.Text)
    key_points_zh = db.Column(db.Text)
    is_free = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class TaiChiUnlock(db.Model):
    """Tracks which user/email has unlocked the full Tai Chi course (post-payment)."""
    __tablename__ = 'tai_chi_unlock'

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(200), nullable=False, index=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    unlocked_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    order = db.relationship('Order', backref='tai_chi_unlocks')
