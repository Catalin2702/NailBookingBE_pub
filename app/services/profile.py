from app.entities.profile import ProfileEntity
from app.services.service import Service


class ProfileService(Service):
	"""
		Profile Service
		ATTRIBUTES:
			entity: ProfileEntity
			actionName: str
			actionParams: dict
		METHODS:
			fulfill_request: fulfill request
			make_response: make response
	"""

	entity: ProfileEntity = ProfileEntity()

	mapped_data = {'actionName'}
	o_mapped_data = {'actionParams'}
