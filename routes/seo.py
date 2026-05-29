"""SEO endpoints: robots.txt and sitemap.xml."""
from flask import Blueprint, Response, url_for, current_app
from datetime import datetime, timezone

seo_bp = Blueprint('seo', __name__)


@seo_bp.route('/robots.txt')
def robots():
    site_url = current_app.config.get('SITE_URL', '').rstrip('/')
    body = (
        "User-agent: *\n"
        "Disallow: /admin/\n"
        "Disallow: /checkout/\n"
        f"Sitemap: {site_url}/sitemap.xml\n"
    )
    return Response(body, mimetype='text/plain')


@seo_bp.route('/sitemap.xml')
def sitemap():
    site_url = current_app.config.get('SITE_URL', '').rstrip('/')
    pages = [
        'main.home', 'main.learn_chinese', 'main.tai_chi',
        'main.custom_trips', 'main.about', 'main.affiliate', 'contact.contact',
    ]
    today = datetime.now(timezone.utc).date().isoformat()
    items = []
    for ep in pages:
        try:
            path = url_for(ep)
            items.append(f'<url><loc>{site_url}{path}</loc><lastmod>{today}</lastmod></url>')
        except Exception:
            continue
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + '\n'.join(items) +
        '\n</urlset>'
    )
    return Response(body, mimetype='application/xml')
