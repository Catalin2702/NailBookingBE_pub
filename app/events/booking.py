from sqlalchemy import event
from asyncio import create_task
from traceback import format_exc

from app.models.booking import BookingModel
from app.services.booking import booking_channel
from app.services.error import ErrorService
from utils.constants import SQLEvents


class BookingEvent:

	@classmethod
	def register_events(cls):
		event.listen(BookingModel, SQLEvents.AFTER_INSERT, cls.booking_after_insert)
		event.listen(BookingModel, SQLEvents.AFTER_UPDATE, cls.booking_after_update)
		event.listen(BookingModel, SQLEvents.AFTER_DELETE, cls.booking_after_delete)

	@staticmethod
	def booking_after_insert(_, __, target):
		# noinspection PyBroadException
		try:
			BookingEvent.send_reload_message(target)
		except Exception:
			ErrorService.save_error(format_exc())

	@staticmethod
	def booking_after_update(_, __, target):
		# noinspection PyBroadException
		try:
			BookingEvent.send_reload_message(target)
		except Exception:
			ErrorService.save_error(format_exc())

	@staticmethod
	def booking_after_delete(_, __, target):
		# noinspection PyBroadException
		try:
			BookingEvent.send_reload_message(target)
		except Exception:
			ErrorService.save_error(format_exc())

	@staticmethod
	def send_reload_message(entity):
		message = {
			'type': 'booking.message',
			'message': {
				'actionName': 'reload',
				'result': {
					'status': True,
					'message': '',
					'content': {
						'id': entity.id,
						'year': entity.year,
						'month': entity.month,
					}
				}
			},
		}
		try:
			create_task(booking_channel.group_send('events.booking', message))
		except RuntimeError:
			pass
