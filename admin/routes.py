from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from extensions import db
from models.affiliate import Affiliate, generate_referral_code
from models.inquiry import Inquiry
from models.commission import Commission
from models.referral_click import ReferralClick
from models.monthly_report import MonthlyReport
from models.page_section import PageSection
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


# ─── CONTENT MANAGEMENT ───

CMS_PAGES = [
    ('index', 'Home', '首页'),
    ('learn_chinese', 'Learn Chinese', '学中文'),
    ('tai_chi', 'Tai Chi', '太极拳'),
    ('custom_trips', 'Custom Trips', '定制旅行'),
    ('about', 'About', '关于我们'),
    ('contact', 'Contact', '联系我们'),
    ('affiliate', 'Affiliate', '推荐分佣'),
]

SECTION_TYPES = ['hero', 'card', 'text_block', 'stats', 'cta', 'gallery', 'testimonial', 'faq']


@admin_bp.route('/content')
@login_required
def content_pages():
    pages_info = []
    for key, en, zh in CMS_PAGES:
        count = PageSection.query.filter_by(page=key).count()
        pages_info.append({'key': key, 'en': en, 'zh': zh, 'count': count})
    return render_template('admin/content/pages.html', pages=pages_info)


@admin_bp.route('/content/<page>')
@login_required
def content_sections(page):
    if page not in [p[0] for p in CMS_PAGES]:
        flash('Unknown page.', 'error')
        return redirect(url_for('admin.content_pages'))
    sections = PageSection.query.filter_by(page=page).order_by(PageSection.sort_order).all()
    page_name = next((p for p in CMS_PAGES if p[0] == page), (page, page, page))
    return render_template('admin/content/sections.html', sections=sections, page=page, page_name=page_name)


@admin_bp.route('/content/<page>/new', methods=['GET', 'POST'])
@login_required
def content_section_new(page):
    if page not in [p[0] for p in CMS_PAGES]:
        return redirect(url_for('admin.content_pages'))
    if request.method == 'POST':
        section = PageSection(
            page=page,
            section_key=request.form.get('section_key', '').strip(),
            section_type=request.form.get('section_type', 'text_block'),
            title_en=request.form.get('title_en', '').strip(),
            title_zh=request.form.get('title_zh', '').strip(),
            subtitle_en=request.form.get('subtitle_en', '').strip(),
            subtitle_zh=request.form.get('subtitle_zh', '').strip(),
            body_en=request.form.get('body_en', '').strip(),
            body_zh=request.form.get('body_zh', '').strip(),
            image_url=request.form.get('image_url', '').strip(),
            button_text_en=request.form.get('button_text_en', '').strip(),
            button_text_zh=request.form.get('button_text_zh', '').strip(),
            button_url=request.form.get('button_url', '').strip(),
            sort_order=int(request.form.get('sort_order') or 0),
            is_visible='is_visible' in request.form,
            extra_data=request.form.get('extra_data', '').strip() or None,
        )
        db.session.add(section)
        db.session.commit()
        flash('Section created.', 'success')
        return redirect(url_for('admin.content_sections', page=page))
    return render_template('admin/content/section_form.html', section=None, page=page, section_types=SECTION_TYPES)


@admin_bp.route('/content/<page>/<section_key>/edit', methods=['GET', 'POST'])
@login_required
def content_section_edit(page, section_key):
    section = PageSection.query.filter_by(page=page, section_key=section_key).first_or_404()
    if request.method == 'POST':
        section.section_type = request.form.get('section_type', section.section_type)
        section.title_en = request.form.get('title_en', '').strip()
        section.title_zh = request.form.get('title_zh', '').strip()
        section.subtitle_en = request.form.get('subtitle_en', '').strip()
        section.subtitle_zh = request.form.get('subtitle_zh', '').strip()
        section.body_en = request.form.get('body_en', '').strip()
        section.body_zh = request.form.get('body_zh', '').strip()
        section.image_url = request.form.get('image_url', '').strip()
        section.button_text_en = request.form.get('button_text_en', '').strip()
        section.button_text_zh = request.form.get('button_text_zh', '').strip()
        section.button_url = request.form.get('button_url', '').strip()
        section.sort_order = int(request.form.get('sort_order') or 0)
        section.is_visible = 'is_visible' in request.form
        section.extra_data = request.form.get('extra_data', '').strip() or None
        db.session.commit()
        flash('Section updated.', 'success')
        return redirect(url_for('admin.content_sections', page=page))
    return render_template('admin/content/section_form.html', section=section, page=page, section_types=SECTION_TYPES)


@admin_bp.route('/content/<page>/<section_key>/toggle', methods=['POST'])
@login_required
def content_section_toggle(page, section_key):
    section = PageSection.query.filter_by(page=page, section_key=section_key).first_or_404()
    section.is_visible = not section.is_visible
    db.session.commit()
    flash(f'Section {"shown" if section.is_visible else "hidden"}.', 'success')
    return redirect(url_for('admin.content_sections', page=page))


@admin_bp.route('/content/<page>/<section_key>/delete', methods=['POST'])
@login_required
def content_section_delete(page, section_key):
    section = PageSection.query.filter_by(page=page, section_key=section_key).first_or_404()
    db.session.delete(section)
    db.session.commit()
    flash('Section deleted.', 'success')
    return redirect(url_for('admin.content_sections', page=page))


@admin_bp.route('/content/<page>/reorder', methods=['POST'])
@login_required
def content_reorder(page):
    items = request.form.getlist('order[]')
    for i, section_id in enumerate(items):
        s = PageSection.query.get(int(section_id))
        if s and s.page == page:
            s.sort_order = i
    db.session.commit()
    return '', 204


@admin_bp.route('/content/seed', methods=['POST'])
@login_required
def content_seed():
    _seed_sections()
    flash('Default content synced to database.', 'success')
    return redirect(url_for('admin.content_pages'))


@admin_bp.route('/content/<page>/seed', methods=['POST'])
@login_required
def content_seed_page(page):
    if page not in [p[0] for p in CMS_PAGES]:
        return redirect(url_for('admin.content_pages'))
    _seed_sections(page)
    flash('Default content synced.', 'success')
    return redirect(url_for('admin.content_sections', page=page))


def _seed_sections(page_filter=None):
    """Seed PageSection records from hardcoded template content."""
    sections = [
        # ── index ──
        ('index', 'hero', 'hero', 0,
         'Discover China. Ancient Wisdom, Modern Access.', '发现中国。千年智慧，触手可及。',
         'Chinese Culture · Global Access', '中国文化 · 全球共享',
         'Learn Mandarin with native teachers, practice Tai Chi with national champions, and explore China on bespoke cultural journeys.', '跟随母语教师学中文，与全国冠军练太极，踏上定制的中国文化之旅。',
         '', 'Start Free Trial', '免费试听', ''),
        ('index', 'tai_chi_preview', 'text_block', 10,
         '24-Form Tai Chi by National Champions', '全国冠军 24式太极拳',
         'Online Course', '在线课程',
         'Often called "meditation in motion." Start with 2 free lessons — experience the ancient art before committing to the full course.', '常被称为"移动的冥想"。前两式免费试看，体验古老养生功法后再决定是否解锁全套。',
         '', 'Start Free Preview', '免费试看', ''),
        ('index', 'destinations', 'text_block', 20,
         'Iconic Places, Unforgettable Experiences', '标志性目的地，难忘的体验',
         'Destinations', '目的地', '', '', '', '', '', ''),
        ('index', 'testimonials', 'text_block', 30,
         'What Travelers Say', '旅行者怎么说',
         'Testimonials', '客户评价', '', '', '', '', '', ''),
        ('index', 'cta_free_pack', 'cta', 40,
         'Ready to Explore China?', '准备好探索中国了吗？',
         'Free Resource Pack', '免费资源包',
         'Get a trial Chinese lesson, Tai Chi PDF guide, and China travel tips — completely free.', '免费领取中文试听课、太极PDF指南和中国旅行攻略。',
         '', 'Get Free Pack', '免费领取', ''),
        # ── learn_chinese ──
        ('learn_chinese', 'hero', 'hero', 0,
         'From Pinyin to Conversation.', '从拼音到日常对话。',
         'Mandarin Courses', '中文课程',
         'Structured courses for kids, adults, and heritage families. Native teachers, proven methods, real results.', '适合儿童、成人及华裔家庭的体系化课程。母语教师，成熟方法，真实效果。',
         '', '', '', ''),
        ('learn_chinese', 'course_categories', 'text_block', 10,
         'Choose Your Path', '选择你的学习路径',
         'Course Categories', '课程分类', '', '', '', '', '', ''),
        ('learn_chinese', 'pricing', 'text_block', 20,
         'Simple, Transparent Pricing', '简单透明的价格',
         'Pricing', '课程价格', '', '', '', '', '', ''),
        ('learn_chinese', 'teachers', 'text_block', 30,
         'Learn from the Best', '向最优秀的老师学习',
         'Our Teachers', '师资展示', '', '', '', '', '', ''),
        ('learn_chinese', 'free_trial', 'cta', 40,
         'Try a Lesson Before You Commit.', '先试听再决定。',
         'Free Trial', '免费试听',
         'Experience our teaching style with a complimentary trial lesson. No credit card, no commitment.', '免费体验我们的教学风格。无需信用卡，无需承诺。',
         '', 'Book Free Trial', '预约免费试听', ''),
        ('learn_chinese', 'teaching_method', 'text_block', 50,
         'How We Teach', '我们的教学方式',
         'Our Approach', '教学方法', '', '', '', '', '', ''),
        # ── tai_chi ──
        ('tai_chi', 'hero', 'hero', 0,
         '24-Form Tai Chi. National Champion Instruction.', '24式太极拳。全国冠军亲自教学。',
         'Online Course', '在线课程',
         '"Meditation in motion" — gentle exercise combining physical movement with mental focus. 2 free lessons to start.', '"移动的冥想"——柔和的体育锻炼与精神专注的结合。前两式免费试看。',
         '', '', '', ''),
        ('tai_chi', 'about_course', 'text_block', 10,
         'Ancient Wisdom, Modern Access.', '古老智慧，触手可及。',
         'About the Course', '课程介绍',
         'Our 24-form Tai Chi course is taught by a national Tai Chi champion. This simplified form was designed for beginners and is perfect for international learners of all ages.', '24式太极拳课程由全国太极拳冠军录制教学。这套简化套路专为初学者设计，适合所有年龄段。',
         '', '', '', ''),
        ('tai_chi', 'pricing', 'text_block', 20,
         'Course Pricing', '课程价格', '', '', '', '', '', '', '', ''),
        ('tai_chi', 'benefits', 'text_block', 30,
         'Why Tai Chi?', '太极的好处', '', '', '', '', '', '', '', ''),
        # ── custom_trips ──
        ('custom_trips', 'hero', 'hero', 0,
         'Your China Journey Starts Here.', '你的中国之旅从这里开始。',
         '10 Curated Packages', '10大经典套餐',
         'Bespoke itineraries with professional photography, local food experiences, and English-speaking guides. From imperial Beijing to the roof of the world.', '专属行程，专业摄影、当地美食体验和英文导游。从皇城北京到世界屋脊。',
         '', '', '', ''),
        ('custom_trips', 'every_trip_includes', 'text_block', 10,
         'Every Package Includes', '每个套餐包含', '', '',
         'All our trips are fully customizable. Mix and match destinations, add experiences, and we\'ll craft the perfect itinerary for you.', '所有行程均可完全定制。自由组合目的地，添加体验项目，我们为您打造完美行程。',
         '', '', '', ''),
        ('custom_trips', 'cta_help', 'cta', 20,
         "Can't Decide? Let Us Help.", '不知道选哪个？让我们来帮你。', '', '',
         'Share your travel dreams with us — we\'ll recommend the perfect package.', '告诉我们你的旅行梦想——我们推荐最适合的套餐。',
         '', 'WhatsApp Us', 'WhatsApp咨询', ''),
        # ── about ──
        ('about', 'hero', 'hero', 0,
         'Bridging Chinese Culture & the World.', '连接中国文化与世界。',
         'About Us', '关于我们', '', '', '', '', '', ''),
        ('about', 'our_story', 'text_block', 10,
         'WuDeRuiBo', '吴德瑞博',
         'Our Story', '品牌故事',
         'A cultural exchange platform founded with a clear mission: to make authentic Chinese culture — language, Tai Chi, and travel — accessible to people worldwide.', '一个文化交流平台，使命是让真正的中国文化——语言、太极拳和旅行——走向全世界。',
         '', '', '', ''),
        ('about', 'philosophy', 'text_block', 20,
         'Our Philosophy', '我们的理念', '', '', '', '', '', '', '', ''),
        ('about', 'cta_free_pack', 'cta', 30,
         'Free Resource Pack', '免费资源包', '', '',
         'Trial Chinese lesson, Tai Chi PDF guide, and China travel tips — all free.', '中文试听课、太极PDF指南和中国旅行攻略——全部免费。',
         '', 'Claim Your Free Pack', '免费领取', ''),
        # ── contact ──
        ('contact', 'hero', 'hero', 0,
         "We'd Love to Hear from You.", '期待您的来信。',
         'Get in Touch', '联系我们',
         'Whether you want to learn Chinese, try Tai Chi, or plan a China trip — we\'re here to help.', '无论您想学中文、练太极还是计划中国旅行——我们随时为您服务。',
         '', '', '', ''),
        # ── affiliate ──
        ('affiliate', 'hero', 'hero', 0,
         'Earn 5-10% Sharing Chinese Culture.', '分享中国文化赚取5-10%佣金。',
         'Partner Program', '合伙人计划',
         'Join our affiliate program and earn commission by sharing authentic Chinese cultural experiences.', '加入推荐分佣计划，分享真正的中国文化体验，赚取佣金。',
         '', '', '', ''),
        ('affiliate', 'how_it_works', 'text_block', 10,
         '4 Simple Steps', '简单4步',
         'How It Works', '运作流程', '', '', '', '', '', ''),
        ('affiliate', 'commission_rates', 'text_block', 20,
         'Commission Rates', '佣金比例', '', '', '', '', '', '', '', ''),
        ('affiliate', 'cta_join', 'cta', 30,
         'Become an Affiliate Partner', '成为推荐合伙人', '', '',
         'Start earning by sharing authentic Chinese culture with the world.', '向世界分享真正的中国文化，开始赚钱。',
         '', 'Apply Now', '立即申请', ''),
    ]

    count = 0
    for row in sections:
        p, key, stype, order = row[0], row[1], row[2], row[3]
        if page_filter and p != page_filter:
            continue
        existing = PageSection.query.filter_by(page=p, section_key=key).first()
        if existing:
            continue
        s = PageSection(
            page=p, section_key=key, section_type=stype, sort_order=order,
            title_en=row[4], title_zh=row[5],
            subtitle_en=row[6], subtitle_zh=row[7],
            body_en=row[8], body_zh=row[9],
            image_url=row[10],
            button_text_en=row[11], button_text_zh=row[12],
            button_url=row[13],
        )
        db.session.add(s)
        count += 1
    db.session.commit()
    return count
