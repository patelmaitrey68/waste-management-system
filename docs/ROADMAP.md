# Project Roadmap & Recommended Folder Layout

This document describes a suggested, minimal roadmap to make the repository layout consistent and easier to maintain.

Goals
- Consolidate templates to a single `templates/` directory (already used by settings) and remove duplicates.
- Keep static vendor files under `static/vendors/` and application static under `static/`.
- Ignore runtime artifacts via `.gitignore`.
- Provide reproducible instructions for running and for optional cleanup operations.

Recommended Folder Layout
- `manage.py` (project entrypoint)
- `waste_management/` (Django project settings, wsgi/asgi)
- `waste/` (Django app: models, views, templates under app if needed)
- `templates/` (single project-level templates directory referenced in settings)
- `static/` (project static; keep `static/vendors/` for 3rd-party vendor files)
- `media/` (uploaded files; ignored in git)
- `docs/` (architecture docs, ROADMAP.md)
- `scripts/` (helper automation and audit scripts)

Action Plan
1. Audit: run `scripts/template_audit.py` to list duplicate and misplaced templates. Inspect results.
2. Consolidate (manual or opt-in): for duplicates, keep one canonical copy in `templates/` and back up others.
3. Replace fragile relative links in templates with named `{% url 'name' %}` tags where possible.
4. Add tests and sample data fixtures for critical flows (Shop, Checkout, Pickup Request).
5. Adopt production practices: move secrets to env vars, set `DEBUG=False`, configure `STATIC_ROOT` and run `collectstatic`.

How to use the audit script
1. Dry-run report:

```bash
python scripts/template_audit.py
```

2. To automatically move duplicate copies into `templates/` (creates backups):

```bash
python scripts/template_audit.py --apply
```

Important: automatic moves can break references; review changes and run the site locally after applying.

If you want, I can run the audit and prepare a concrete consolidation patch we can apply safely.
