from django.http import JsonResponse

from app.services.booking import BookingService


def confirm_booking(_, confirm_code: str):
	return JsonResponse(BookingService.confirm_booking_by_code(confirm_code), safe=False)

def booked_booking(_, booked_code: str):
	return JsonResponse(BookingService.booked_booking_by_code(booked_code), safe=False)

def generate_new_booking(_, action_code: str) -> JsonResponse:
	return JsonResponse(BookingService.generate_new_booking(action_code), safe=False)

def request_new_booking(_, action_code: str) -> JsonResponse:
	return JsonResponse(BookingService.request_new_booking(action_code), safe=False)
