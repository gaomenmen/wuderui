from extensions import db
from datetime import datetime, timezone


class ReferralClick(db.Model):
    __tablename__ = 'referral_click'

    id = db.Column(db.Integer, primary_key=True)
    affiliate_id = db.Column(db.Integer, db.ForeignKey('affiliate.id'), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    landing_page = db.Column(db.String(200))
    clicked_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
