from uuid import uuid4
from sqlalchemy import Column, ForeignKey, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import deferred

from app.models.base import Model, Base


class ActionModel(Model, Base):
	"""
		Action Model
		ATTRIBUTES:
			id: Integer
			type: String(20)
			params: JSONB
			id_mail: Integer
			code: String(36)
			upd_datetime: DateTime(timezone=True)
	"""

	__tablename__ = 'actions'

	id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
	type = Column(String(20), nullable=False)
	params = Column(JSONB, nullable=False)
	id_mail = Column(Integer, ForeignKey('mails.id', onupdate='CASCADE'), nullable=True)
	code = Column(String(36), nullable=False)
	upd_datetime = deferred(Column(DateTime(timezone=True), nullable=False))

	def __init__(self, _type, params, id_mail=None, code=None, upd_datetime=func.now()):
		super().__init__()
		self.type = _type
		self.params = params
		self.id_mail = id_mail
		self.upd_datetime = upd_datetime
		self.code = code or str(uuid4())
