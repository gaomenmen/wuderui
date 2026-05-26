from extensions import db
from datetime import datetime, timezone


class Commission(db.Model):
    __tablename__ = 'commission'

    SERVICE_TYPES = ['chinese', 'taichi', 'travel']
    STATUS_CHOICES = ['pending', 'approved', 'paid']

    id = db.Column(db.Integer, primary_key=True)
    affiliate_id = db.Column(db.Integer, db.ForeignKey('affiliate.id'), nullable=False)
    inquiry_id = db.Column(db.Integer, db.ForeignKey('inquiry.id'), nullable=False)
    service_type = db.Column(db.String(20), nullable=False)
    sale_amount = db.Column(db.Float, nullable=False)
    commission_rate = db.Column(db.Float, nullable=False)
    commission_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    inquiry = db.relationship('Inquiry', backref='commissions')
