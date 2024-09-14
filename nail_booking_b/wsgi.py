import os

from django.core.wsgi import get_wsgi_application, WSGIHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nail_booking_b.settings')

application: WSGIHandler = get_wsgi_application()
