from os import environ

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from app.consumers.routing import urlpatterns
from app.cronjobs.cron import Cron
from app.events.event import Event

environ.setdefault("DJANGO_SETTINGS_MODULE", "nail_booking_b.settings")

application: ProtocolTypeRouter = ProtocolTypeRouter(
	{
		"http": get_asgi_application(),
		"websocket": AllowedHostsOriginValidator(
			URLRouter(
				urlpatterns
			)
		),
	}
)

Cron.start_process()
Event.start_process()
