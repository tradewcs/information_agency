# information_agency

A Django-based web application for managing and delivering structured information services.

## 🚀 Project Overview

`information_agency` is a Django project scaffolded to provide a solid foundation for building data-driven web applications, APIs, and back-office administration for information management.

## ✅ Key Features

- Django project structure with separate settings for production
- Ready-to-use Django app under `temp/` with models, views, and admin integration
- Built-in Django ORM migrations for schema management

## 🧰 Prerequisites

- Python 3.11+ (or the version your environment requires)
- pip (Python package manager)
- Virtual environment tool (recommended): `venv`, `virtualenv`, or `pipenv`

## ⚙️ Installation

1. Clone the repository:

```bash
git clone <repo-url> information_agency
cd information_agency
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## 🧩 Configuration

Copy the sample settings (if provided) or configure environment variables for your deployment.

Example (Unix/macOS):

```bash
export DJANGO_SETTINGS_MODULE=information_agency.settings.prod
```

## ▶️ Running the Development Server

```bash
python manage.py migrate
python manage.py runserver
```

Then visit `http://127.0.0.1:8000/` in your browser.

## 🧪 Running Tests

```bash
python manage.py test
```

## 📦 Deployment

For production deployments, ensure:

- `DEBUG = False`
- Proper secret management (environment variables / secret manager)
- Static files are collected (`python manage.py collectstatic`)
- A WSGI server like Gunicorn / uWSGI is used behind a reverse proxy
