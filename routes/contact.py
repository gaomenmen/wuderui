from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from models.inquiry import Inquiry
from models.affiliate import Affiliate

contact_bp = Blueprint('contact', __name__)


def get_locale():
    lang = request.args.get('lang')
    if lang in ['en', 'zh']:
        session['lang'] = lang
    if 'lang' in session:
        return session['lang']
    return 'en'


@contact_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        interests_list = request.form.getlist('interests')
        interests = ','.join(interests_list)
        message = request.form.get('message', '').strip()
        manual_ref = request.form.get('referral_code', '').strip()
        source_page = request.form.get('source_page', 'contact')

        if not name or not email:
            flash('Name and email are required.', 'error')
            return redirect(url_for('contact.contact'))

        cookie_ref = request.cookies.get('wdr_ref')
        ref_code = cookie_ref or manual_ref or None

        affiliate_id = None
        if ref_code:
            aff = Affiliate.query.filter_by(referral_code=ref_code, status='active').first()
            if aff:
                affiliate_id = aff.id

        inquiry = Inquiry(
            name=name,
            email=email,
            phone=phone,
            interests=interests,
            message=message,
            referral_code=ref_code,
            affiliate_id=affiliate_id,
            source_page=source_page,
        )
        db.session.add(inquiry)
        db.session.commit()

        flash('Thank you! We\'ll get back to you soon.', 'success')
        return redirect(url_for('contact.contact'))

    return render_template('contact.html')
