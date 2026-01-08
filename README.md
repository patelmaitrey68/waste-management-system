WASTE_MANAGEMENT — Local development helper

Quick start:

1. Activate the venv and install dependencies:

```bash
cd /Users/maitreypatel/Downloads/WASTE_MANAGEMENT
source .venv/bin/activate
pip install -r requirements.txt
```

2. Start the app (this script applies migrations then runs the dev server):

```bash
./run.sh
```

Admin: a superuser `admin` was created during setup (password `admin123`) — change it in production.

Notes and full instructions

- Required software and versions

	- Python 3.9+ (this repo was validated with Python 3.9.6). Use `python --version` to confirm.
	- A virtualenv (recommended). The project includes a `.venv/` in the repo used for development.
	- The project uses Django (see `requirements.txt`). `Pillow` is required for image fields.

- Database

	- By default the project is configured to use MySQL in production. For local development the project will prefer `db.sqlite3` if present. No extra database server is required for local testing.

- Installing dependencies

```bash
cd /Users/maitreypatel/Downloads/WASTE_MANAGEMENT
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# If you don't have a requirements file, install at least:
# pip install Django==4.2.1 pillow
```

- Apply migrations and create the admin user

```bash
source .venv/bin/activate
python manage.py migrate
# If you want to create the default admin user (already created in this workspace):
# python manage.py createsuperuser
```

- Run the development server

```bash
./run.sh
# or directly:
python manage.py runserver 0.0.0.0:8000
```

- Admin account (development)

	- Username: `admin`
	- Password: `admin123`

- Fixtures / sample data

	- A small products fixture is available at `waste/fixtures/sample_products.json`.
	- Load it with:

```bash
python manage.py loaddata waste/fixtures/sample_products.json
```

- Static and media files

	- `STATICFILES_DIRS` points to the project `static/` directory. For production set `STATIC_ROOT` and run `python manage.py collectstatic`.
	- Uploaded files are stored under `media/` (see `MEDIA_ROOT`) and are ignored via `.gitignore`.

- Template / project cleanup utilities

	- `scripts/template_audit.py` — scans project and app template folders for duplicate/misplaced templates and can consolidate them into `templates/`.
	- `docs/ROADMAP.md` — recommended project layout and next steps.

- Troubleshooting

	- If pages return 404s from incorrect relative links, the templates were updated to use absolute paths and base hrefs; run the audit script to detect duplicates.
	- If the dev server won't start because the port is in use: stop the running process (or run on a different port):

```bash
python manage.py runserver 0.0.0.0:8001
```

Contributing / next steps

- If you want me to further tidy templates I can:
	- Replace recurring relative `href` values with `{% url 'route_name' %}` (requires mapping route names).
	- Consolidate templates and remove empty template folders (I can prepare a safe patch).

If you'd like, I can now run a smoke test (visit `/`, `/Shop`, `/user/Shop`, `/admin/`) and report results.
