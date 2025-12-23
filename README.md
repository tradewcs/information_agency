(Website)[https://information-agency-fjbz.onrender.com]

# information_agency

A lightweight Django CMS for collaborative newspapers and publishers —
focused on editor workflows, invites, and simple content management. ✅

---

## 🚀 Quick Start

1. Clone the repo and create a virtual environment (Windows example):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1    # PowerShell
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

## 🐞 Troubleshooting — Invite duplicates

If you see duplicate invites created after a single click, check these places:

- Server-side: `core/views.py` — `create_newspaper_invite` (transaction, select_for_update,
  duplicate checks, and logging)
- Client-side: `templates/core/newspaper_detail.html` — modal submit handler
  (guard against double-binding and disabled submit during AJAX)
- Tests: `core/tests.py` — view tests that cover invite creation and
  duplicate-rejection behavior

Enable server logs and open your browser DevTools (Network & Console) to see
whether two POST requests are being sent, or whether a race condition occurs
server-side.

---

## 🤝 Contributing

- Fork, create a feature branch, add tests for new behavior, and open a PR.
- Keep lines wrapped to 79–88 characters and add docstrings for public views.

---

## 📄 License

MIT (add LICENSE file if needed)

---

Happy hacking! ✨