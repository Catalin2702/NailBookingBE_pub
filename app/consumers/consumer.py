from channels.generic.websocket import AsyncWebsocketConsumer


class Consumer(AsyncWebsocketConsumer):
	"""
		Consumer
		ATTRIBUTES:
			identifier: str
		METHODS:
			connect: connect
			disconnect: disconnect
			receive: receive
	"""
	identifier: str = ''

	async def connect(self):
		"""
			Called when the websocket is handshaking as part of initial connection.
		"""
		await self.accept()

	async def disconnect(self, close_code: int = None):
		"""
			Called when the WebSocket closes for any reason.
			:param close_code: Int
		"""
		for attr in self.__dict__:
			setattr(self, attr, None)

	async def receive(self, text_data: str = None, bytes_data: bytes = None):
		"""
			Called when a message is received with either text or bytes
			:param text_data: str
			:param bytes_data: bytes
		"""
		raise NotImplementedError

	@staticmethod
	def response(action: str, result: any) -> dict:
		"""
			Response
			:param action: str
			:param result: any
			:return: dict
		"""
		return {
			'actionName': action,
			'result': result
		}
