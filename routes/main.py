from flask import Blueprint, render_template, request, g, session
from extensions import babel
from models.affiliate import Affiliate
from models.referral_click import ReferralClick
from models.teacher import Teacher
from models.chinese_course import ChineseCourse
from models.tai_chi_lesson import TaiChiLesson
from models.trip_package import TripPackage

main_bp = Blueprint('main', __name__)


def get_locale():
    lang = request.args.get('lang')
    if lang in ['en', 'zh']:
        session['lang'] = lang
    if 'lang' in session:
        return session['lang']
    return 'en'


@main_bp.before_app_request
def track_referral():
    ref_code = request.args.get('ref')
    if ref_code:
        from extensions import db
        affiliate = Affiliate.query.filter_by(referral_code=ref_code, status='active').first()
        if affiliate:
            click = ReferralClick(
                affiliate_id=affiliate.id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')[:500],
                landing_page=request.path
            )
            db.session.add(click)
            db.session.commit()
            g.set_ref_cookie = ref_code


@main_bp.after_app_request
def set_referral_cookie(response):
    ref_code = g.pop('set_ref_cookie', None)
    if ref_code:
        response.set_cookie('wdr_ref', ref_code, max_age=2592000, httponly=True, samesite='Lax')
    return response


@main_bp.route('/')
def home():
    return render_template('index.html')


@main_bp.route('/learn-chinese')
def learn_chinese():
    teachers = Teacher.query.filter_by(is_active=True).order_by(Teacher.sort_order).all()
    courses = ChineseCourse.query.filter_by(is_active=True).order_by(ChineseCourse.sort_order).all()
    return render_template('learn_chinese.html', teachers=teachers, courses=courses)


@main_bp.route('/tai-chi')
def tai_chi():
    lessons = TaiChiLesson.query.filter_by(is_active=True).order_by(TaiChiLesson.number).all()
    return render_template('tai_chi.html', lessons=lessons)


@main_bp.route('/custom-trips')
def custom_trips():
    packages = TripPackage.query.filter_by(is_active=True).order_by(TripPackage.sort_order).all()
    return render_template('custom_trips.html', packages=packages)


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/affiliate')
def affiliate():
    return render_template('affiliate.html')

