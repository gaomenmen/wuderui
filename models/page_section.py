from extensions import db
from datetime import datetime, timezone
import json


class PageSection(db.Model):
    __tablename__ = 'page_section'

    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(50), nullable=False)
    section_key = db.Column(db.String(50), nullable=False)
    section_type = db.Column(db.String(20), nullable=False, default='text_block')
    title_en = db.Column(db.String(200))
    title_zh = db.Column(db.String(200))
    subtitle_en = db.Column(db.String(200))
    subtitle_zh = db.Column(db.String(200))
    body_en = db.Column(db.Text)
    body_zh = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    button_text_en = db.Column(db.String(100))
    button_text_zh = db.Column(db.String(100))
    button_url = db.Column(db.String(500))
    sort_order = db.Column(db.Integer, default=0)
    is_visible = db.Column(db.Boolean, default=True)
    extra_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint('page', 'section_key'),)

    def get_extra(self):
        if self.extra_data:
            try:
                return json.loads(self.extra_data)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    def set_extra(self, data):
        self.extra_data = json.dumps(data, ensure_ascii=False)
