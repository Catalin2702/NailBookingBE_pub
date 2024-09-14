from typing import Union

from app.entities.cleaner import CleanerEntity
from app.services.service import Service


class CleanerService(Service):
	"""
		Cleaner Service
		ATTRIBUTES:
			entity: CleanerEntity
			actionName: str
			actionParams: dict
		METHODS:
			fulfill_request: fulfill request
			make_response: make response
	"""

	entity: CleanerEntity = CleanerEntity()

	mapped_data = {'actionName'}
	o_mapped_data = {'actionParams'}

	@classmethod
	def clean_actions(cls) -> dict[str, Union[bool, str, dict]]:
		return cls.entity.clean_actions()

	@classmethod
	def clean_mails(cls) -> dict[str, Union[bool, str, dict]]:
		return cls.entity.clean_mails()

	@classmethod
	def clean_confirmations(cls) -> dict[str, Union[bool, str, dict]]:
		return cls.entity.clean_confirmations()

	@classmethod
	def clean_errors(cls) -> dict[str, Union[bool, str, dict]]:
		return cls.entity.clean_errors()

	@classmethod
	def clean_sessions(cls) -> dict[str, Union[bool, str, dict]]:
		return cls.entity.clean_sessions()
