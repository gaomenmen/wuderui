from extensions import db
from datetime import datetime, timezone
from sqlalchemy import func


class MonthlyReport(db.Model):
    __tablename__ = 'monthly_report'

    id = db.Column(db.Integer, primary_key=True)
    affiliate_id = db.Column(db.Integer, db.ForeignKey('affiliate.id'), nullable=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    total_clicks = db.Column(db.Integer, default=0)
    total_inquiries = db.Column(db.Integer, default=0)
    total_commissions = db.Column(db.Integer, default=0)
    total_commission_amount = db.Column(db.Float, default=0.0)
    total_paid = db.Column(db.Float, default=0.0)
    generated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    affiliate = db.relationship('Affiliate', backref='monthly_reports')

    @staticmethod
    def generate(year, month, affiliate_id=None):
        from models.referral_click import ReferralClick
        from models.inquiry import Inquiry
        from models.commission import Commission

        query_affiliate_id = affiliate_id

        start = datetime(year, month, 1, tzinfo=timezone.utc)
        if month == 12:
            end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end = datetime(year, month + 1, 1, tzinfo=timezone.utc)

        clicks_q = ReferralClick.query.filter(ReferralClick.clicked_at >= start, ReferralClick.clicked_at < end)
        inquiries_q = Inquiry.query.filter(Inquiry.created_at >= start, Inquiry.created_at < end)
        commissions_q = Commission.query.filter(Commission.created_at >= start, Commission.created_at < end)

        if query_affiliate_id:
            clicks_q = clicks_q.filter_by(affiliate_id=query_affiliate_id)
            inquiries_q = inquiries_q.filter_by(affiliate_id=query_affiliate_id)
            commissions_q = commissions_q.filter_by(affiliate_id=query_affiliate_id)

        report = MonthlyReport.query.filter_by(year=year, month=month, affiliate_id=query_affiliate_id).first()
        if not report:
            report = MonthlyReport(year=year, month=month, affiliate_id=query_affiliate_id)
            db.session.add(report)

        report.total_clicks = clicks_q.count()
        report.total_inquiries = inquiries_q.count()
        report.total_commissions = commissions_q.count()
        report.total_commission_amount = commissions_q.with_entities(func.coalesce(func.sum(Commission.commission_amount), 0)).scalar() or 0
        report.total_paid = commissions_q.filter(Commission.status == 'paid').with_entities(func.coalesce(func.sum(Commission.commission_amount), 0)).scalar() or 0
        report.generated_at = datetime.now(timezone.utc)

        db.session.commit()
        return report
