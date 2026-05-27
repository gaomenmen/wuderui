import os
import pytest

os.environ['FLASK_SKIP_DB_CREATE'] = '1'

from app import create_app
from extensions import db as _db


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config['WTF_CSRF_ENABLED'] = False
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_client(client, app):
    from models.admin_user import AdminUser
    admin = AdminUser(username='testadmin')
    admin.set_password('testpass123')
    _db.session.add(admin)
    _db.session.commit()
    client.post('/admin/login', data={'username': 'testadmin', 'password': 'testpass123'})
    return client
