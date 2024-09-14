from django.urls import path

from app.views.action import confirm_email, confirm_join_account
from app.views.booking import confirm_booking, booked_booking, generate_new_booking, request_new_booking

urlpatterns = [
	path(r'action/confirm_email/<str:action_code>/', confirm_email, name='confirm_email'),
	path(r'action/join_account/<str:action_code>/', confirm_join_account, name='confirm_join_account'),

	path(r'booking/confirm_booking/<str:confirm_code>/', confirm_booking, name='confirm_booking'),
	path(r'booking/book_booking/<str:booked_code>/', booked_booking, name='booked_booking'),
	path(r'booking/new_booking/<str:action_code>/', generate_new_booking, name='generate_new_booking'),
	path(r'booking/request_new_booking/<str:action_code>/', request_new_booking, name='request_new_booking'),
]
