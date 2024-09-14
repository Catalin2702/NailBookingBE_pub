from json import loads
from traceback import format_exc

from app.services.account import AccountService
from app.services.context import Context
from app.consumers.consumer import Consumer
from utils.tools import response
from utils.messages import Errors


class AccountConsumer(AccountService, Consumer):
	"""
		Account Consumer
		ATTRIBUTES:
			entity: AccountEntity
			actionName: str
			actionParams: dict
		METHODS:
			fulfill_request: fulfill request
			make_response: make response
			connect: connect
			disconnect: disconnect
			receive: receive
	"""

	async def disconnect(self, close_code: int = None):
		if self.identifier in Context:
			del Context[self.identifier]
		await self.channel_layer.group_discard('events.account', self.channel_name)
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
			if data['actionName'] == 'login' and result['status']:
				self.identifier = result['content']['identifier']

			response_data = self.response(data['actionName'], result)

		except Exception:
			self.entity.save_error(format_exc())
			response_data = self.response(data['actionName'], response(False, Errors.GENERIC_ERROR))

		await self.send(self.make_response(response_data))
