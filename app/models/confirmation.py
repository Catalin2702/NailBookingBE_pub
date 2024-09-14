from uuid import uuid4
from sqlalchemy import Column, ForeignKey, DateTime, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.orm import deferred

from app.models.base import Model, Base


class ConfirmationModel(Model, Base):
	"""
		Confirmation Model
		ATTRIBUTES:
			id: Integer
			type: String(20)
			id_booking: Integer
			id_mail: Integer
			code: String(36)
			upd_datetime: DateTime(timezone=True)
	"""

	__tablename__ = 'confirmations'

	id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
	type = Column(String(20), nullable=False)
	id_booking = Column(Integer, ForeignKey('booking.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
	id_mail = Column(Integer, ForeignKey('mails.id', onupdate='CASCADE'), nullable=True)
	code = Column(String(36), nullable=False)
	upd_datetime = deferred(Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()))

	def __init__(self, _type, id_booking, id_mail=None, code=None, upd_datetime=func.now()):
		super().__init__()
		self.type = _type
		self.id_booking = id_booking
		self.id_mail = id_mail
		self.upd_datetime = upd_datetime
		self.code = code or str(uuid4())
