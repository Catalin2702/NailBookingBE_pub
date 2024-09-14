from traceback import format_exc
from sqlalchemy import Column, Text, DateTime, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import deferred

from app.models.base import Model, Base
from utils.tools import print_error
from utils.env import SettingsEnv


class ErrorModel(Model, Base):
	"""
		Error Model
		ATTRIBUTES:
			id: Integer
			error: Text
			upd_datetime: DateTime
	"""

	__tablename__ = 'errors'

	id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
	error = Column(Text, nullable=False)
	upd_datetime = deferred(Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now()))

	def __init__(self, error, update_time = func.now()):
		super().__init__()
		self.error = error
		self.upd_datetime = update_time

	@classmethod
	def save_error(cls, error: str):
		# noinspection PyBroadException
		try:
			if not error:
				error = format_exc()
			if SettingsEnv.RUNNING_MODE.is_dev:
				print_error(error)
			else:
				cls(error).save()
		except:
			print_error(format_exc())
