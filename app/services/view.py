from typing import Union

from views.utils import create_view
from app.services.service import Service
from app.entities.error import ErrorEntity


class ViewService(Service):
	"""
		View Service
		ATTRIBUTES:
			viewName: str
			actionName: str
			viewParams: dict
			actionParams: dict
		METHODS:
			fulfill_request: fulfill request
			make_response: make response
	"""

	viewName: str = ''
	viewParams: dict = {}

	mapped_data = {'viewName', 'actionName', 'actionParams'}

	async def fulfill_request(self, data: dict) -> dict[str, Union[bool, str, dict]]:
		self.set_attr_from_data(data)
		return await create_view(self.viewName, **self.viewParams).execute(self.actionName, **self.actionParams)

	@staticmethod
	def save_error(error: str = None):
		"""
			Save an error
			:param error: str
			:return: dict
		"""
		ErrorEntity.save_error(error)
