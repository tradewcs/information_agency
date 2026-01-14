from .base import *


DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# DATABASES = {
#     "default": dj_database_url.parse(
#         os.environ.get("DATABASE_URL"),
#         "postgresql://pg:1111@localhost:5432/information_agency",
#         conn_max_age=600,
#         ssl_require=True,
#     )
# }

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
