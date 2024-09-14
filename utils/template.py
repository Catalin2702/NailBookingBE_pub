from datetime import date, time, datetime
from traceback import format_exc
from typing import Union

from sqlalchemy.orm.session import Session

from app.models.base import Model
from app.models.error import ErrorModel
from utils.tools import response
from utils.messages import Errors


class Mapper:

	_method_mapping = {}

	def __init__(self, **kwargs):
		for key, value in kwargs.items():
			if key == 'mapping':
				self._method_mapping[self.__class__.__name__] = value
			else:
				setattr(self, key, value)

	async def execute(self, method_name: str, **kwargs) -> dict[str, Union[bool, str, dict]]:
		# noinspection PyBroadException
		try:
			return await self._method_mapping[self.__class__.__name__][method_name](**kwargs)
		except KeyError:
			self.save_error(f'Error in {self.__class__.__name__}.{method_name}: Method not found\n{"\n".join("{key}: {value}".format(key=key, value=value) for key, value in kwargs.items())}')
			return self.default()
		except Exception:
			self.save_error(f'Error in {self.__class__.__name__}.{method_name}:\n{"\n".join("{key}: {value}".format(key=key, value=value) for key, value in kwargs.items())}\n{format_exc()}')
			return self.default()

	# noinspection PyUnusedLocal
	@staticmethod
	def default() -> dict[str, Union[bool, str, dict]]:
		return response(False, Errors.GENERIC_ERROR)

	@staticmethod
	def get_session(commit=True) -> Session:
		"""
			Get Session
			:param commit: bool
			:return: Session
		"""
		# noinspection PyTypeChecker
		return Model.get_session(commit)

	@staticmethod
	def result_to_dict(res: object) -> dict:
		"""
			Return a dict from a result object.
		"""
		return {key: value for key, value in res.__dict__.items() if not key.startswith('_')}

	@staticmethod
	def results_to_dict(res: list) -> list[dict[str, Union[str, int, date, time, datetime, bool]]]:
		"""
			Return a list of dict from a result list
		"""
		return list(map(lambda x: Mapper.result_to_dict(x), res))

	@classmethod
	def save_error(cls, error):
		ErrorModel.save_error(error)
