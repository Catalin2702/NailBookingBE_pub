from django.urls import path

from app.consumers.view import ViewConsumer
from app.consumers.booking import BookingConsumer
from app.consumers.account import AccountConsumer
from app.consumers.profile import ProfileConsumer

urlpatterns = [
	path(r"ws/view/", ViewConsumer.as_asgi()),
	path(r"ws/booking/", BookingConsumer.as_asgi()),
	path(r"ws/account/", AccountConsumer.as_asgi()),
	path(r"ws/profile/", ProfileConsumer.as_asgi()),
]
