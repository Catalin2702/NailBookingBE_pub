from traceback import format_exc

from app.services.error import ErrorService
from utils.env import SettingsEnv


class Job:

	def __init__(self, **kwargs):
		for key, value in kwargs.items():
			setattr(self, key, value)

	def main(self):
		raise NotImplementedError('Method main not implemented')

	def __call__(self):
		self.main()

	@staticmethod
	def log(func: callable):
		def wrapper(*args, **kwargs):
			# noinspection PyBroadException
			try:
				if SettingsEnv.RUNNING_MODE.is_dev:
					if args and hasattr(args[0], '__class__'):
						print(f'Running: {args[0].__class__.__name__}.{func.__name__}')
					else:
						print(f'Running: {func.__name__}')
				return func(*args, **kwargs)
			except Exception:
				ErrorService.save_error(format_exc())
		return wrapper
