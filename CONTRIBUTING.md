# Contributing to WuDeRuiBo

Thank you for your interest in contributing!

## Quick Start

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Make your changes
4. Run tests: `pytest`
5. Submit a Pull Request

## Development Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install pytest  # for running tests
flask run
```

## Code Style

- Follow PEP 8 for Python
- Use 4-space indentation
- Keep functions focused and small
- Jinja2 templates use bilingual pattern: `<span class="en">English</span><span class="zh">中文</span>`

## Branch Naming

| Type | Format | Example |
|------|--------|---------|
| Feature | `feat/description` | `feat/add-blog-page` |
| Bug fix | `fix/description` | `fix/contact-form-validation` |
| Docs | `docs/description` | `docs/update-api-guide` |
| Refactor | `refactor/description` | `refactor/simplify-cms-routes` |

## Pull Request Process

1. One feature per PR — keep it focused
2. Update README if you add/change user-facing functionality
3. Add tests for new business logic
4. Ensure all existing tests pass: `pytest`
5. The PR will be reviewed before merging

## Reporting Issues

Open a GitHub Issue with:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Python version and OS

## Project Structure

```
app.py              — Application factory
config.py           — Configuration
models/             — SQLAlchemy models
routes/             — Public page routes
admin/routes.py     — Admin panel routes
templates/          — Jinja2 templates (bilingual)
```

## Bilingual Content

All user-facing text uses the dual-span pattern:

```html
<span class="en">English text</span><span class="zh">中文文本</span>
```

When adding new pages or sections, always include both languages.

## License

By contributing, you agree that your contributions will be licensed under the Apache-2.0 License.
