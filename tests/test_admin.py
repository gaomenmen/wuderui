from extensions import db
from models.page_section import PageSection


def test_admin_content_seed(admin_client, app):
    with app.app_context():
        resp = admin_client.post('/admin/content/seed', follow_redirects=True)
        assert resp.status_code == 200
        assert PageSection.query.count() > 0


def test_admin_create_section(admin_client, app):
    with app.app_context():
        resp = admin_client.post('/admin/content/index/new', data={
            'section_key': 'test_new',
            'section_type': 'text_block',
            'title_en': 'Test Section',
            'title_zh': '测试版块',
            'sort_order': 99,
            'is_visible': 'on',
        }, follow_redirects=True)
        assert resp.status_code == 200
        section = PageSection.query.filter_by(page='index', section_key='test_new').first()
        assert section is not None
        assert section.title_en == 'Test Section'


def test_admin_toggle_section(admin_client, app):
    with app.app_context():
        section = PageSection(page='index', section_key='toggle_test',
                              section_type='text_block', is_visible=True)
        db.session.add(section)
        db.session.commit()

        resp = admin_client.post('/admin/content/index/toggle_test/toggle', follow_redirects=True)
        assert resp.status_code == 200
        section = PageSection.query.filter_by(page='index', section_key='toggle_test').first()
        assert section.is_visible is False


def test_admin_delete_section(admin_client, app):
    with app.app_context():
        section = PageSection(page='index', section_key='delete_test',
                              section_type='text_block')
        db.session.add(section)
        db.session.commit()

        resp = admin_client.post('/admin/content/index/delete_test/delete', follow_redirects=True)
        assert resp.status_code == 200
        assert PageSection.query.filter_by(page='index', section_key='delete_test').first() is None
