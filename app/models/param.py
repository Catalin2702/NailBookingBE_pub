from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import deferred

from app.models.base import Model, Base


class ParamModel(Model, Base):
	"""
		Param Model
		ATTRIBUTES:
			key: String(255)
			value: String(255)
			description: String(255)
		METHODS:
			__init__: init
			__repr__: repr
			get_all: get all
			get: get
	"""

	__tablename__: str = 'params'

	key = Column(String(255), primary_key=True, nullable=False)
	value = Column(String(255), nullable=False)
	description = deferred(Column(String(255), nullable=True, default=None))
	upd_datetime = deferred(Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()))

	def __init__(self, key, value, description = None, upd_datetime = func.now()):
		super().__init__()
		self.key = key
		self.value = value
		self.description = description
		self.upd_datetime = upd_datetime
