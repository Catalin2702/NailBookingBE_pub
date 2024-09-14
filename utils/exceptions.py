from traceback import format_exc

from utils.env import SettingsEnv
from utils.tools import print_error
from app.services.error import ErrorService


def exception(value=None):
	def inner_decorator(func):
		def wrapper(*args, **kwargs):
			# noinspection PyBroadException
			try:
				return func(*args, **kwargs)
			except Exception:
				if SettingsEnv.RUNNING_MODE.is_dev:
					print_error(format_exc())
				else:
					ErrorService.save_error(format_exc())
				return value

		return wrapper

	return inner_decorator
