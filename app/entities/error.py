from app.entities.entity import Entity


class ErrorEntity(Entity):

	def __init__(self, **kwargs):
		kwargs['mapping'] = {
			'saveError': 'save_error'
		}
		super().__init__(**kwargs)

	@classmethod
	def save_error(cls, error: str = ''):
		# noinspection PyBroadException
		cls.Error.save_error(error)
