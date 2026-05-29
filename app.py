import os
import click
from flask import Flask, render_template
from config import Config
from extensions import db, login_manager, babel, migrate, csrf


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
    csrf.init_app(app)

    app.jinja_env.globals['get_locale'] = get_locale

    from models.page_section import PageSection
    app.jinja_env.globals['cms_section'] = lambda page, key: PageSection.query.filter_by(page=page, section_key=key, is_visible=True).first()
    app.jinja_env.globals['cms_sections'] = lambda page: PageSection.query.filter_by(page=page, is_visible=True).order_by(PageSection.sort_order).all()

    # Make SEO + analytics config available to all templates
    @app.context_processor
    def _inject_site_globals():
        return {
            'GA_ID': app.config.get('GOOGLE_ANALYTICS_ID', ''),
            'CLARITY_ID': app.config.get('MICROSOFT_CLARITY_ID', ''),
            'SITE_URL': app.config.get('SITE_URL', ''),
            'SITE_NAME': app.config.get('SITE_NAME', 'WuDeRuiBo'),
        }

    from routes.main import main_bp
    from routes.contact import contact_bp
    from routes.auth import auth_bp
    from routes.checkout import checkout_bp
    from routes.seo import seo_bp
    from admin.routes import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(seo_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        if not os.environ.get('FLASK_SKIP_DB_CREATE'):
            db.create_all()
            _ensure_admin(app)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app


def _ensure_admin(app):
    """Create the default admin user *only* if no admin exists.

    Notes:
      * Once an admin row exists, this function is a no-op — changing
        ADMIN_PASSWORD in the environment will NOT overwrite a user-set
        password. This is by design so production secrets are stable.
      * If a rebuild *loses* the database (e.g. SQLite file not on a
        persistent volume), the default admin will be re-created. Make sure
        the `instance/` directory is mounted as a persistent volume in
        containers, or use PostgreSQL via DATABASE_URL.
    """
    from models.admin_user import AdminUser
    password = os.environ.get('ADMIN_PASSWORD', 'changeme123')
    if AdminUser.query.first() is None:
        admin = AdminUser(username='admin', must_change_password=True)
        admin.password_hash = __import__('werkzeug.security', fromlist=['generate_password_hash']).generate_password_hash(password)
        db.session.add(admin)
        db.session.commit()
        app.logger.warning(
            'Default admin user created: admin / %s — please log in and change immediately. '
            'If you see this message after every redeploy, your database is not persisted.',
            password,
        )
    else:
        app.logger.info('Admin user already exists; ADMIN_PASSWORD env var is ignored.')


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


@app.cli.command('reset-admin-password')
@click.argument('username')
@click.argument('new_password')
def reset_admin_password(username, new_password):
    """Reset password for an existing admin user (avoids deleting the DB)."""
    from models.admin_user import AdminUser
    user = AdminUser.query.filter_by(username=username).first()
    if user is None:
        click.echo(f'User {username} not found.')
        return
    user.set_password(new_password)
    db.session.commit()
    click.echo(f'Password reset for {username}.')


@app.cli.command('seed-content')
def seed_content():
    """Seed default Tai Chi lessons, trip packages, teachers, courses, and CMS sections."""
    from admin.routes import _seed_sections
    from admin.seed_data import seed_tai_chi, seed_trips, seed_teachers, seed_chinese_courses
    n_sec = _seed_sections()
    n_lessons = seed_tai_chi()
    n_trips = seed_trips()
    n_teachers = seed_teachers()
    n_courses = seed_chinese_courses()
    click.echo(f'Seeded: {n_sec} CMS sections, {n_lessons} Tai Chi lessons, '
               f'{n_trips} trip packages, {n_teachers} teachers, {n_courses} Chinese courses.')


if __name__ == '__main__':
    app.run(debug=True)

