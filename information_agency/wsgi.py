import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "information_agency.settings.prod")

application = get_wsgi_application()
