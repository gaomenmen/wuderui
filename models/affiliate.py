from extensions import db
from datetime import datetime, timezone
import secrets
import string


def generate_referral_code():
    chars = string.ascii_uppercase + string.digits
    while True:
        code = 'WDR-' + ''.join(secrets.choice(chars) for _ in range(4))
        if not Affiliate.query.filter_by(referral_code=code).first():
            return code


class Affiliate(db.Model):
    __tablename__ = 'affiliate'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(40))
    referral_code = db.Column(db.String(20), unique=True, nullable=False)
    commission_rate_chinese = db.Column(db.Float, default=0.05)
    commission_rate_taichi = db.Column(db.Float, default=0.08)
    commission_rate_travel = db.Column(db.Float, default=0.10)
    status = db.Column(db.String(20), default='active')
    paypal_email = db.Column(db.String(120))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    clicks = db.relationship('ReferralClick', backref='affiliate', lazy='dynamic')
    inquiries = db.relationship('Inquiry', backref='affiliate', lazy='dynamic')
    commissions = db.relationship('Commission', backref='affiliate', lazy='dynamic')

    def get_rate(self, service_type):
        return {
            'chinese': self.commission_rate_chinese,
            'taichi': self.commission_rate_taichi,
            'travel': self.commission_rate_travel,
        }.get(service_type, 0)
