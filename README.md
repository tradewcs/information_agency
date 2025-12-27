(Website)[https://information-agency-fjbz.onrender.com]

# information_agency

A lightweight Django CMS for collaborative newspapers and publishers —
focused on editor workflows, invites, and simple content management. ✅

---

## 🚀 Quick Start

1. Clone the repo and create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Apply migrations and create a superuser:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

3. Run the development server:

   ```bash
   python manage.py runserver
   ```

4. Open http://127.0.0.1:8000/ in your browser.

---

## ✨ Features

- **Publishers** (custom user model) with registration & email verification
- **Topics** and **Newspapers** with a Summernote rich-text editor
- **Invite-to-newspaper** workflow (token-based invites + email)
- Inline AJAX invite modal with pending-invites partial
- Access controls: editors vs. read-only users
- Tests and basic linting (pytest / flake8)

---

## 🧭 Commands & Tests

- Run the Django test suite:

  ```bash
  python manage.py test
  ```

- Lint the `core` app:

  ```bash
  flake8 .\core\
  ```

- Run style checks and auto-formatting as needed (project-specific tools may
  be used).

---

## ⚙️ Environment & Configuration

This project expects a few environment variables for production (SMTP, SECRET
key, etc.). Locally you can configure them in a `.env` file or set them in
your environment. Typical vars:

- `DJANGO_SECRET_KEY` — secret key
- `DEBUG` — `True`/`False`
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`

---

