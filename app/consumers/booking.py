from json import loads
from traceback import format_exc

from app.consumers.consumer import Consumer
from app.services.booking import BookingService
from utils.tools import response
from utils.messages import Errors


class BookingConsumer(BookingService, Consumer):
	"""
		Booking Consumer
		ATTRIBUTES:
			entity: BookingEntity
			actionName: str
			actionParams: dict
		METHODS:
			fulfill_request: fulfill request
			make_response: make response
			connect: connect
			disconnect: disconnect
			receive: receive
			booking_message: booking message
	"""

	async def connect(self):
		await self.channel_layer.group_add('events.booking', self.channel_name)
		await super().connect()

	async def disconnect(self, close_code: int = None):
		await self.channel_layer.group_discard('events.booking', self.channel_name)
		await super().disconnect(close_code)

	async def receive(self, text_data: str = None, bytes_data: bytes = None):
		"""
			Called when a message is received with either text or bytes
			:param text_data: str
			:param bytes_data: bytes
		"""
		data = {
			'actionName': '',
		}
		# noinspection PyBroadException
		try:
			data: dict = loads(text_data)
			result = await self.fulfill_request(data)
			response_data = self.response(data['actionName'], result)

		except Exception:
			self.entity.save_error(format_exc())
			response_data = self.response(data['actionName'], response(False, Errors.GENERIC_ERROR))
		await self.send(self.make_response(response_data))

	async def booking_message(self, _event):
		"""
			Used by group_send to send a message to group
		"""
		await self.send(self.make_response(_event['message']))
