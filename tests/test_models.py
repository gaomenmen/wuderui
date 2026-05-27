from extensions import db
from models.admin_user import AdminUser
from models.affiliate import Affiliate, generate_referral_code
from models.inquiry import Inquiry
from models.commission import Commission
from models.page_section import PageSection


def test_admin_password_hashing(app):
    with app.app_context():
        admin = AdminUser(username='test')
        admin.set_password('mypassword')
        assert admin.check_password('mypassword') is True
        assert admin.check_password('wrong') is False


def test_affiliate_get_rate(app):
    with app.app_context():
        aff = Affiliate(
            name='Test Partner', email='test@example.com',
            referral_code='WDR-TEST',
            commission_rate_chinese=0.05,
            commission_rate_taichi=0.08,
            commission_rate_travel=0.10,
        )
        assert aff.get_rate('chinese') == 0.05
        assert aff.get_rate('taichi') == 0.08
        assert aff.get_rate('travel') == 0.10
        assert aff.get_rate('unknown') == 0


def test_commission_calculation(app):
    with app.app_context():
        aff = Affiliate(name='Test', email='t@t.com', referral_code='WDR-COM',
                        commission_rate_travel=0.10)
        db.session.add(aff)
        db.session.commit()

        inquiry = Inquiry(name='John', email='john@test.com')
        db.session.add(inquiry)
        db.session.commit()

        sale = 10000
        rate = aff.get_rate('travel')
        commission = Commission(
            affiliate_id=aff.id, inquiry_id=inquiry.id,
            service_type='travel', sale_amount=sale,
            commission_rate=rate, commission_amount=round(sale * rate, 2),
        )
        db.session.add(commission)
        db.session.commit()

        assert commission.commission_amount == 1000.0
        assert commission.status == 'pending'


def test_page_section_extra_data(app):
    with app.app_context():
        section = PageSection(
            page='index', section_key='test_section',
            section_type='text_block',
            title_en='Test', title_zh='测试',
        )
        section.set_extra({'tags': ['a', 'b'], 'count': 5})
        db.session.add(section)
        db.session.commit()

        loaded = PageSection.query.filter_by(page='index', section_key='test_section').first()
        extra = loaded.get_extra()
        assert extra['tags'] == ['a', 'b']
        assert extra['count'] == 5


def test_page_section_visibility(app):
    with app.app_context():
        visible = PageSection(page='index', section_key='visible',
                              section_type='text_block', is_visible=True)
        hidden = PageSection(page='index', section_key='hidden',
                             section_type='text_block', is_visible=False)
        db.session.add_all([visible, hidden])
        db.session.commit()

        assert PageSection.query.filter_by(page='index', section_key='visible', is_visible=True).first() is not None
        assert PageSection.query.filter_by(page='index', section_key='hidden', is_visible=True).first() is None
