from json import loads
from traceback import format_exc

from app.services.view import ViewService
from .consumer import Consumer


class ViewConsumer(ViewService, Consumer):
	"""
		View Consumer
		ATTRIBUTES:
			viewName: str
			actionName: str
			viewParams: dict
			actionParams: dict
		METHODS:
			fulfill_request: fulfill request
			make_response: make response
			connect: connect
			disconnect: disconnect
			receive: receive
	"""

	async def receive(self, text_data: str = None, bytes_data: bytes = None):
		"""
			Receive message from WebSocket
			:param text_data: str
			:param bytes_data: bytes
			:return: None
		"""
		data = {
			'actionName': '',
		}
		# noinspection PyBroadException
		try:
			data: dict = loads(text_data)
			res = await self.fulfill_request(data)

			response = {
				'viewName': self.viewName,
				'actionName': self.actionName,
				'result': res,
			}
		except Exception:
			self.save_error(format_exc())
			response = {
				'viewName': data['viewName'],
				'actionName': data['actionName'],
				'result': '',
			}
		await self.send(self.make_response(response))
