from json import dumps
from traceback import format_exc

from utils.tools import print_error


class Service:
	entity: None
	actionName: str = ''
	actionParams: dict = {}
	mapped_data: set[str] = set()
	o_mapped_data: set[str] = set()

	async def fulfill_request(self, data: dict):
		self.set_attr_from_data(data)
		return await self.entity.execute(self.actionName, **self.actionParams)


	def set_attr_from_data(self, data: dict):
		"""
			Set attributes from data
			:param data: dict
		"""
		try:
			for key in self.mapped_data:
				setattr(self, key, data[key])
			for key in self.o_mapped_data:
				setattr(self, key, data.get(key, getattr(self, key)))

		except KeyError:
			print_error(format_exc())

	@staticmethod
	def make_response(data: dict) -> str:
		"""
			Make response
			:param data: dict
			:return: str
		"""
		return dumps(data, default=str)
