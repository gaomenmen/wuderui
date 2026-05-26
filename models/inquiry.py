from extensions import db
from datetime import datetime, timezone


class Inquiry(db.Model):
    __tablename__ = 'inquiry'

    STATUS_CHOICES = ['new', 'contacted', 'converted', 'closed']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    interests = db.Column(db.String(200))
    message = db.Column(db.Text)
    referral_code = db.Column(db.String(20))
    affiliate_id = db.Column(db.Integer, db.ForeignKey('affiliate.id'))
    source_page = db.Column(db.String(100))
    status = db.Column(db.String(20), default='new')
    estimated_value = db.Column(db.Float)
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
