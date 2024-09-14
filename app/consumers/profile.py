from traceback import format_exc
from json import loads

from app.consumers.consumer import Consumer
from app.services.profile import ProfileService
from utils.tools import response
from utils.messages import Errors


class ProfileConsumer(ProfileService, Consumer):
	"""
		Profile Consumer
		ATTRIBUTES:
			entity: ProfileEntity
			actionName: str
			actionParams: dict
		METHODS:
			fulfill_request: fulfill request
			make_response: make response
			connect: connect
			disconnect: disconnect
			receive: receive
	"""

	async def connect(self):
		await super().connect()

	async def disconnect(self, close_code: int = None):
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
