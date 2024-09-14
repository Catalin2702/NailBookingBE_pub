from typing import Union

from app.services.service import Service
from app.entities.error import ErrorEntity


class ErrorService(Service):
	"""
		Error Service
		ATTRIBUTES:
			entity: ErrorEntity
			actionName: str
			actionParams: dict
		METHODS:
			fulfill_request: fulfill request
			make_response: make response
	"""

	entity: ErrorEntity = ErrorEntity()

	mapped_data = {'actionName'}
	o_mapped_data = {'actionParams'}

	@classmethod
	def save_error(cls, error: Union[str, Exception] = None):
		"""
			Save an error
			:param error: str
			:return: dict
		"""
		if isinstance(error, Exception):
			error = str(error)
		cls.entity.save_error(error)
