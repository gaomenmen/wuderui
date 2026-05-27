import os
import click
from flask import Flask
from config import Config
from extensions import db, login_manager, babel, migrate


def get_locale():
    from flask import request, session
    lang = request.args.get('lang')
    if lang in ['en', 'zh']:
        session['lang'] = lang
    if 'lang' in session:
        return session['lang']
    return 'en'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if uri.startswith('postgres://'):
        app.config['SQLALCHEMY_DATABASE_URI'] = uri.replace('postgres://', 'postgresql://', 1)

    db.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app, locale_selector=get_locale)
    migrate.init_app(app, db)

    app.jinja_env.globals['get_locale'] = get_locale

    from models.page_section import PageSection
    app.jinja_env.globals['cms_section'] = lambda page, key: PageSection.query.filter_by(page=page, section_key=key, is_visible=True).first()
    app.jinja_env.globals['cms_sections'] = lambda page: PageSection.query.filter_by(page=page, is_visible=True).order_by(PageSection.sort_order).all()

    from routes.main import main_bp
    from routes.contact import contact_bp
    from routes.auth import auth_bp
    from admin.routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        if not os.environ.get('FLASK_SKIP_DB_CREATE'):
            db.create_all()
            _ensure_admin(app)

    return app


def _ensure_admin(app):
    from models.admin_user import AdminUser
    password = os.environ.get('ADMIN_PASSWORD', 'changeme123')
    if AdminUser.query.first() is None:
        admin = AdminUser(username='admin', must_change_password=True)
        admin.password_hash = __import__('werkzeug.security', fromlist=['generate_password_hash']).generate_password_hash(password)
        db.session.add(admin)
        db.session.commit()
        app.logger.info('Default admin created: admin / %s — change password immediately!', password)


app = create_app()


@app.cli.command('create-admin')
@click.argument('username')
@click.argument('password')
def create_admin(username, password):
    from models.admin_user import AdminUser
    if AdminUser.query.filter_by(username=username).first():
        click.echo(f'User {username} already exists.')
        return
    admin = AdminUser(username=username)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    click.echo(f'Admin user {username} created.')


if __name__ == '__main__':
    app.run(debug=True)
