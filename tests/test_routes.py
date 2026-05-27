from extensions import db
from models.inquiry import Inquiry
from models.affiliate import Affiliate


def test_contact_form_submission(client, app):
    with app.app_context():
        resp = client.post('/contact', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '123456',
            'interests': ['chinese', 'travel'],
            'message': 'I want to learn Chinese',
            'source_page': 'contact',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert Inquiry.query.count() == 1
        inquiry = Inquiry.query.first()
        assert inquiry.name == 'Test User'
        assert 'chinese' in inquiry.interests
        assert 'travel' in inquiry.interests


def test_contact_form_requires_name_and_email(client, app):
    with app.app_context():
        resp = client.post('/contact', data={
            'name': '',
            'email': '',
        }, follow_redirects=True)
        assert resp.status_code == 200
        assert Inquiry.query.count() == 0


def test_contact_form_referral_cookie(client, app):
    with app.app_context():
        aff = Affiliate(name='Partner', email='p@test.com', referral_code='WDR-REF', status='active')
        db.session.add(aff)
        db.session.commit()

        client.set_cookie('wdr_ref', 'WDR-REF')
        resp = client.post('/contact', data={
            'name': 'Referred User',
            'email': 'referred@test.com',
        }, follow_redirects=True)
        assert resp.status_code == 200
        inquiry = Inquiry.query.first()
        assert inquiry.affiliate_id == aff.id
        assert inquiry.referral_code == 'WDR-REF'


def test_public_pages_accessible(client):
    pages = ['/', '/learn-chinese', '/tai-chi', '/custom-trips', '/about', '/contact', '/affiliate']
    for page in pages:
        resp = client.get(page)
        assert resp.status_code == 200, f'{page} returned {resp.status_code}'


def test_admin_login(client, app):
    with app.app_context():
        from models.admin_user import AdminUser
        admin = AdminUser(username='logintest')
        admin.set_password('pass123')
        db.session.add(admin)
        db.session.commit()

    resp = client.post('/admin/login', data={
        'username': 'logintest',
        'password': 'pass123',
    }, follow_redirects=True)
    assert resp.status_code == 200


def test_admin_requires_login(client):
    resp = client.get('/admin/', follow_redirects=False)
    assert resp.status_code == 302
    assert '/admin/login' in resp.headers['Location']
