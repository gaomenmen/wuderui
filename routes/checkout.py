"""Checkout flow: create PayPal orders and handle return/capture."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
from extensions import db
from models.order import Order, Payment, generate_order_no
from models.tai_chi_lesson import TaiChiLesson, TaiChiUnlock
from models.chinese_course import ChineseCourse
from models.trip_package import TripPackage
from models.affiliate import Affiliate
from services import paypal
from datetime import datetime, timezone
import json

checkout_bp = Blueprint('checkout', __name__, url_prefix='/checkout')


def _resolve_item(item_type, item_id):
    """Return (label, default_amount) for a purchasable item."""
    if item_type == 'taichi_full':
        return ('24-Form Tai Chi Course (Full Unlock)', 99.0)
    if item_type == 'taichi_lesson':
        lesson = TaiChiLesson.query.get_or_404(item_id)
        return (f'Tai Chi Lesson #{lesson.number} — {lesson.name_en}', 9.99)
    if item_type == 'chinese_course':
        course = ChineseCourse.query.get_or_404(item_id)
        return (course.name_en, float(course.price or 0))
    if item_type == 'trip_deposit':
        pkg = TripPackage.query.get_or_404(item_id)
        return (f'Deposit — {pkg.title_en}', 200.0)
    abort(404)


@checkout_bp.route('/<item_type>')
@checkout_bp.route('/<item_type>/<int:item_id>')
def checkout_form(item_type, item_id=None):
    """Display a small form collecting email then redirecting to PayPal."""
    if item_type not in Order.ITEM_TYPES:
        abort(404)
    label, amount = _resolve_item(item_type, item_id or 0)
    return render_template('checkout/start.html',
                           item_type=item_type, item_id=item_id,
                           label=label, amount=amount,
                           currency=current_app.config.get('PAYPAL_CURRENCY', 'USD'),
                           paypal_configured=paypal.is_configured())


@checkout_bp.route('/<item_type>/start', methods=['POST'])
@checkout_bp.route('/<item_type>/<int:item_id>/start', methods=['POST'])
def checkout_start(item_type, item_id=None):
    if item_type not in Order.ITEM_TYPES:
        abort(404)
    email = (request.form.get('email') or '').strip()
    name = (request.form.get('name') or '').strip()
    if '@' not in email:
        flash('Please provide a valid email.', 'error')
        return redirect(url_for('checkout.checkout_form', item_type=item_type, item_id=item_id))

    label, amount = _resolve_item(item_type, item_id or 0)
    currency = current_app.config.get('PAYPAL_CURRENCY', 'USD')

    ref_code = request.cookies.get('wdr_ref')
    affiliate = Affiliate.query.filter_by(referral_code=ref_code, status='active').first() if ref_code else None

    order = Order(
        order_no=generate_order_no(),
        user_email=email, user_name=name,
        item_type=item_type, item_id=item_id,
        item_label=label, amount=amount, currency=currency,
        status='created',
        referral_code=ref_code if affiliate else None,
        affiliate_id=affiliate.id if affiliate else None,
    )
    db.session.add(order)
    db.session.commit()

    if not paypal.is_configured():
        flash('Payment is not yet configured. Your order has been recorded — '
              'we will contact you by email to complete payment manually.', 'warning')
        return redirect(url_for('checkout.success', order_no=order.order_no))

    return_url = url_for('checkout.paypal_return', order_no=order.order_no, _external=True)
    cancel_url = url_for('checkout.paypal_cancel', order_no=order.order_no, _external=True)

    try:
        resp = paypal.create_order(amount, currency, return_url, cancel_url, reference=order.order_no)
        order.paypal_order_id = resp.get('id')
        order.status = 'pending_payment'
        db.session.commit()
        approval = paypal.approval_link(resp)
        if approval:
            return redirect(approval)
        flash('Could not get PayPal approval link.', 'error')
    except paypal.PayPalNotConfigured:
        flash('PayPal is not configured.', 'error')
    except paypal.PayPalError as e:
        current_app.logger.error('PayPal create order failed: %s', e)
        flash('Payment provider error. Please try again later.', 'error')

    return redirect(url_for('checkout.checkout_form', item_type=item_type, item_id=item_id))


@checkout_bp.route('/return/<order_no>')
def paypal_return(order_no):
    order = Order.query.filter_by(order_no=order_no).first_or_404()
    if not order.paypal_order_id:
        flash('Missing PayPal order id.', 'error')
        return redirect(url_for('main.home'))
    try:
        capture = paypal.capture_order(order.paypal_order_id)
        status = capture.get('status', '').upper()
        payment = Payment(
            order_id=order.id, provider='paypal',
            transaction_id=capture.get('id'),
            amount=order.amount, currency=order.currency,
            status=status, raw_payload=json.dumps(capture)[:5000],
            captured_at=datetime.now(timezone.utc),
        )
        db.session.add(payment)
        if status == 'COMPLETED':
            order.status = 'paid'
            order.paid_at = datetime.now(timezone.utc)
            _post_payment_actions(order)
        else:
            order.status = 'failed'
        db.session.commit()
    except paypal.PayPalError as e:
        current_app.logger.error('PayPal capture failed: %s', e)
        order.status = 'failed'
        db.session.commit()
        flash('Payment capture failed.', 'error')
        return redirect(url_for('checkout.failure', order_no=order.order_no))

    return redirect(url_for('checkout.success', order_no=order.order_no))


@checkout_bp.route('/cancel/<order_no>')
def paypal_cancel(order_no):
    order = Order.query.filter_by(order_no=order_no).first_or_404()
    if order.status in ('created', 'pending_payment'):
        order.status = 'cancelled'
        db.session.commit()
    flash('Payment was cancelled.', 'warning')
    return redirect(url_for('main.home'))


@checkout_bp.route('/success/<order_no>')
def success(order_no):
    order = Order.query.filter_by(order_no=order_no).first_or_404()
    return render_template('checkout/success.html', order=order)


@checkout_bp.route('/failure/<order_no>')
def failure(order_no):
    order = Order.query.filter_by(order_no=order_no).first_or_404()
    return render_template('checkout/failure.html', order=order)


def _post_payment_actions(order):
    """Run side effects after an order is paid: unlock content, record commission."""
    # Unlock Tai Chi full course
    if order.item_type == 'taichi_full':
        if not TaiChiUnlock.query.filter_by(user_email=order.user_email).first():
            db.session.add(TaiChiUnlock(user_email=order.user_email, order_id=order.id))

    # Record affiliate commission
    if order.affiliate_id:
        from models.commission import Commission
        from models.affiliate import Affiliate
        affiliate = Affiliate.query.get(order.affiliate_id)
        service_type_map = {
            'taichi_full': 'taichi',
            'taichi_lesson': 'taichi',
            'chinese_course': 'chinese',
            'trip_deposit': 'travel',
            'membership': 'chinese',
        }
        svc = service_type_map.get(order.item_type, 'chinese')
        rate = affiliate.get_rate(svc) or 0
        if rate > 0:
            commission = Commission(
                affiliate_id=affiliate.id,
                order_id=order.id,
                service_type=svc,
                sale_amount=order.amount,
                commission_rate=rate,
                commission_amount=round(order.amount * rate, 2),
                status='pending',
            )
            db.session.add(commission)
