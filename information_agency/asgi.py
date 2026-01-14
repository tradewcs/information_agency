import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "information_agency.settings.prod")

application = get_asgi_application()
