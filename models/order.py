from extensions import db
from datetime import datetime, timezone
import secrets


def generate_order_no():
    return 'WDR-' + datetime.now(timezone.utc).strftime('%Y%m%d') + '-' + secrets.token_hex(3).upper()


class Order(db.Model):
    __tablename__ = 'order'

    ITEM_TYPES = ['taichi_full', 'taichi_lesson', 'chinese_course', 'trip_deposit', 'membership']
    STATUSES = ['created', 'pending_payment', 'paid', 'failed', 'cancelled', 'refunded']

    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(40), unique=True, nullable=False, default=generate_order_no)
    user_email = db.Column(db.String(200), nullable=False, index=True)
    user_name = db.Column(db.String(120))
    item_type = db.Column(db.String(40), nullable=False)
    item_id = db.Column(db.Integer)
    item_label = db.Column(db.String(200))
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    status = db.Column(db.String(20), default='created')
    paypal_order_id = db.Column(db.String(120))
    referral_code = db.Column(db.String(20))
    affiliate_id = db.Column(db.Integer, db.ForeignKey('affiliate.id'))
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    affiliate = db.relationship('Affiliate', backref='orders')
    payments = db.relationship('Payment', backref='order', lazy='dynamic', cascade='all, delete-orphan')


class Payment(db.Model):
    __tablename__ = 'payment'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    provider = db.Column(db.String(20), nullable=False, default='paypal')  # paypal | stripe
    transaction_id = db.Column(db.String(200))
    amount = db.Column(db.Float)
    currency = db.Column(db.String(10), default='USD')
    status = db.Column(db.String(40))
    raw_payload = db.Column(db.Text)
    captured_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
