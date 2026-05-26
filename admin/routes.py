from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from extensions import db
from models.affiliate import Affiliate, generate_referral_code
from models.inquiry import Inquiry
from models.commission import Commission
from models.referral_click import ReferralClick
from models.monthly_report import MonthlyReport
from datetime import datetime, timezone
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@login_required
def dashboard():
    now = datetime.now(timezone.utc)
    month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)

    total_inquiries = Inquiry.query.count()
    month_inquiries = Inquiry.query.filter(Inquiry.created_at >= month_start).count()
    new_inquiries = Inquiry.query.filter_by(status='new').count()
    active_affiliates = Affiliate.query.filter_by(status='active').count()
    pending_commissions = Commission.query.filter(Commission.status.in_(['pending', 'approved'])).all()
    pending_total = sum(c.commission_amount for c in pending_commissions)
    month_commission_total = db.session.query(func.coalesce(func.sum(Commission.commission_amount), 0)).filter(
        Commission.created_at >= month_start
    ).scalar() or 0

    recent_inquiries = Inquiry.query.order_by(Inquiry.created_at.desc()).limit(8).all()
    recent_commissions = Commission.query.order_by(Commission.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
        total_inquiries=total_inquiries,
        month_inquiries=month_inquiries,
        new_inquiries=new_inquiries,
        active_affiliates=active_affiliates,
        pending_total=pending_total,
        month_commission_total=month_commission_total,
        recent_inquiries=recent_inquiries,
        recent_commissions=recent_commissions,
    )


# ─── INQUIRIES ───

@admin_bp.route('/inquiries')
@login_required
def inquiries():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    aff_id = request.args.get('affiliate_id', type=int)
    q = Inquiry.query
    if status:
        q = q.filter_by(status=status)
    if aff_id:
        q = q.filter_by(affiliate_id=aff_id)
    inquiries = q.order_by(Inquiry.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/inquiries.html', inquiries=inquiries, status=status, affiliate_id=aff_id)


@admin_bp.route('/inquiries/<int:id>', methods=['GET', 'POST'])
@login_required
def inquiry_detail(id):
    inquiry = Inquiry.query.get_or_404(id)
    if request.method == 'POST':
        inquiry.status = request.form.get('status', inquiry.status)
        inquiry.estimated_value = float(request.form.get('estimated_value') or 0) or None
        inquiry.admin_notes = request.form.get('admin_notes', '')
        db.session.commit()
        flash('Inquiry updated.', 'success')
        return redirect(url_for('admin.inquiry_detail', id=id))
    return render_template('admin/inquiry_detail.html', inquiry=inquiry)


# ─── AFFILIATES ───

@admin_bp.route('/affiliates')
@login_required
def affiliates():
    affiliates = Affiliate.query.order_by(Affiliate.created_at.desc()).all()
    return render_template('admin/affiliates.html', affiliates=affiliates)


@admin_bp.route('/affiliates/new', methods=['GET', 'POST'])
@admin_bp.route('/affiliates/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def affiliate_form(id=None):
    affiliate = Affiliate.query.get_or_404(id) if id else None
    if request.method == 'POST':
        if affiliate is None:
            affiliate = Affiliate(referral_code=generate_referral_code())
            db.session.add(affiliate)
        affiliate.name = request.form.get('name', '').strip()
        affiliate.email = request.form.get('email', '').strip()
        affiliate.phone = request.form.get('phone', '').strip()
        affiliate.paypal_email = request.form.get('paypal_email', '').strip()
        affiliate.commission_rate_chinese = float(request.form.get('rate_chinese') or 5) / 100
        affiliate.commission_rate_taichi = float(request.form.get('rate_taichi') or 8) / 100
        affiliate.commission_rate_travel = float(request.form.get('rate_travel') or 10) / 100
        affiliate.status = request.form.get('status', 'active')
        affiliate.notes = request.form.get('notes', '')
        db.session.commit()
        flash('Affiliate saved.', 'success')
        return redirect(url_for('admin.affiliate_detail', id=affiliate.id))
    return render_template('admin/affiliate_form.html', affiliate=affiliate)


@admin_bp.route('/affiliates/<int:id>')
@login_required
def affiliate_detail(id):
    affiliate = Affiliate.query.get_or_404(id)
    clicks = ReferralClick.query.filter_by(affiliate_id=id).order_by(ReferralClick.clicked_at.desc()).limit(50).all()
    inquiries = Inquiry.query.filter_by(affiliate_id=id).order_by(Inquiry.created_at.desc()).all()
    commissions = Commission.query.filter_by(affiliate_id=id).order_by(Commission.created_at.desc()).all()
    total_earned = sum(c.commission_amount for c in commissions)
    total_paid = sum(c.commission_amount for c in commissions if c.status == 'paid')
    return render_template('admin/affiliate_detail.html',
        affiliate=affiliate, clicks=clicks, inquiries=inquiries,
        commissions=commissions, total_earned=total_earned, total_paid=total_paid)


# ─── COMMISSIONS ───

@admin_bp.route('/commissions')
@login_required
def commissions():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    q = Commission.query
    if status:
        q = q.filter_by(status=status)
    commissions = q.order_by(Commission.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/commissions.html', commissions=commissions, status=status)


@admin_bp.route('/commissions/new', methods=['GET', 'POST'])
@login_required
def commission_new():
    if request.method == 'POST':
        inquiry_id = request.form.get('inquiry_id', type=int)
        service_type = request.form.get('service_type')
        sale_amount = float(request.form.get('sale_amount') or 0)
        inquiry = Inquiry.query.get_or_404(inquiry_id)

        if not inquiry.affiliate_id:
            flash('This inquiry has no affiliate.', 'error')
            return redirect(url_for('admin.commission_new'))

        affiliate = Affiliate.query.get(inquiry.affiliate_id)
        rate = affiliate.get_rate(service_type)

        commission = Commission(
            affiliate_id=affiliate.id,
            inquiry_id=inquiry.id,
            service_type=service_type,
            sale_amount=sale_amount,
            commission_rate=rate,
            commission_amount=round(sale_amount * rate, 2),
        )
        db.session.add(commission)
        db.session.commit()
        flash('Commission created.', 'success')
        return redirect(url_for('admin.commissions'))

    inquiries = Inquiry.query.filter(Inquiry.affiliate_id.isnot(None)).order_by(Inquiry.created_at.desc()).all()
    return render_template('admin/commission_form.html', inquiries=inquiries)


@admin_bp.route('/commissions/<int:id>/approve', methods=['POST'])
@login_required
def commission_approve(id):
    c = Commission.query.get_or_404(id)
    c.status = 'approved'
    db.session.commit()
    flash('Commission approved.', 'success')
    return redirect(url_for('admin.commissions'))


@admin_bp.route('/commissions/bulk-pay', methods=['POST'])
@login_required
def commission_bulk_pay():
    ids = request.form.getlist('commission_ids')
    now = datetime.now(timezone.utc)
    count = 0
    for cid in ids:
        c = Commission.query.get(int(cid))
        if c and c.status != 'paid':
            c.status = 'paid'
            c.paid_at = now
            count += 1
    db.session.commit()
    flash(f'{count} commission(s) marked as paid.', 'success')
    return redirect(url_for('admin.commissions', status='pending'))


# ─── REPORTS ───

@admin_bp.route('/reports')
@login_required
def reports():
    reports = MonthlyReport.query.order_by(MonthlyReport.year.desc(), MonthlyReport.month.desc()).all()
    affiliates = Affiliate.query.filter_by(status='active').all()
    return render_template('admin/reports.html', reports=reports, affiliates=affiliates)


@admin_bp.route('/reports/generate', methods=['POST'])
@login_required
def report_generate():
    year = request.form.get('year', type=int)
    month = request.form.get('month', type=int)
    aff_id = request.form.get('affiliate_id', type=int)

    if not year or not month:
        flash('Year and month required.', 'error')
        return redirect(url_for('admin.reports'))

    if aff_id:
        MonthlyReport.generate(year, month, aff_id)
    else:
        for aff in Affiliate.query.filter_by(status='active').all():
            MonthlyReport.generate(year, month, aff.id)
        MonthlyReport.generate(year, month, None)

    flash('Report generated.', 'success')
    return redirect(url_for('admin.reports'))


# ─── SETTLEMENTS ───

@admin_bp.route('/settlements')
@login_required
def settlements():
    page = request.args.get('page', 1, type=int)
    paid = Commission.query.filter_by(status='paid').order_by(Commission.paid_at.desc()).paginate(page=page, per_page=20, error_out=False)
    total_paid = db.session.query(func.coalesce(func.sum(Commission.commission_amount), 0)).filter_by(status='paid').scalar() or 0
    return render_template('admin/settlements.html', paid=paid, total_paid=total_paid)
