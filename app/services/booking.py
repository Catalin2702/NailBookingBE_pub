from channels.layers import get_channel_layer
from typing import Union

from app.entities.booking import BookingEntity
from app.services.service import Service


class BookingService(Service):
	"""
		Booking Service
		ATTRIBUTES:
			entity: BookingEntity
			actionName: str
			actionParams: dict
		METHODS:
			fulfill_request: fulfill request
			make_response: make response
	"""

	entity: BookingEntity = BookingEntity()

	mapped_data = {'actionName'}
	o_mapped_data = {'actionParams'}

	@classmethod
	async def cancel_booking(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		return await cls.entity.cancel_booking(**kwargs)

	@classmethod
	async def get_booking(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		return await cls.entity.get_booking(**kwargs)

	@classmethod
	async def edit_booking(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		return await cls.entity.edit_booking(**kwargs)

	@classmethod
	def confirm_booking_by_code(cls, confirm_code: str) -> dict[str, Union[bool, str, dict]]:
		return cls.entity.confirm_booking_by_code(confirm_code)

	@classmethod
	def booked_booking_by_code(cls, booked_code: str) -> dict[str, Union[bool, str, dict]]:
		return cls.entity.accept_booking_by_code(booked_code)

	@classmethod
	def complete_bookings(cls) -> dict[str, Union[bool, str, dict]]:
		return cls.entity.complete_bookings()

	@classmethod
	def generate_new_booking(cls, action_code: str) -> dict[str, Union[bool, str, dict]]:
		return cls.entity.generate_new_booking(action_code)

	@classmethod
	def request_new_booking(cls, action_code: str) -> dict[str, Union[bool, str, dict]]:
		return cls.entity.request_new_booking(action_code)

	@classmethod
	async def get_booking_internal_data(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		return await cls.entity.get_booking_internal_data(**kwargs)

	@classmethod
	async def edit_booking_internal_data(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		return await cls.entity.edit_booking_internal_data(**kwargs)

	@classmethod
	async def get_all_booking_data(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		return await cls.entity.get_all_booking_data(**kwargs)


booking_channel = get_channel_layer()
