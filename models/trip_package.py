from extensions import db
from datetime import datetime, timezone


class TripPackage(db.Model):
    __tablename__ = 'trip_package'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    title_zh = db.Column(db.String(200))
    destination_en = db.Column(db.String(200))
    destination_zh = db.Column(db.String(200))
    days = db.Column(db.Integer)
    price_min = db.Column(db.Float)
    price_max = db.Column(db.Float)
    currency = db.Column(db.String(10), default='USD')
    audience_en = db.Column(db.String(200))
    audience_zh = db.Column(db.String(200))
    highlights_en = db.Column(db.Text)
    highlights_zh = db.Column(db.Text)
    services_en = db.Column(db.Text)
    services_zh = db.Column(db.Text)
    cover_image = db.Column(db.String(500))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
