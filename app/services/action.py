from app.entities.action import ActionEntity
from app.services.service import Service


class ActionService(Service):
	"""
		Action Service
		ATTRIBUTES:
			entity: ActionEntity
			actionName: str
			actionParams: dict
		METHODS:
			fulfill_request: fulfill request
			make_response: make response
	"""

	entity: ActionEntity = ActionEntity()

	mapped_data = {'actionName'}
	o_mapped_data = {'actionParams'}

	@classmethod
	def confirm_email(cls, action_code: str) -> dict:
		return cls.entity.confirm_email(action_code)

	@classmethod
	def confirm_join_account(cls, action_code: str) -> dict:
		return cls.entity.confirm_join_account(action_code)
