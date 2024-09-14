from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import deferred
from typing import Sequence

from app.models.base import Model, Base


class BookingNoteModel(Model, Base):
	"""
		BookingNote Model
		ATTRIBUTES:
			id: Integer
			id_booking: Integer
			note: Text
			upd_datetime: DateTime
	"""

	__tablename__ = 'booking_notes'

	id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
	id_booking = Column(Integer, ForeignKey('booking.id', onupdate='CASCADE'), nullable=False)
	note = Column(Text, nullable=False)
	upd_datetime = deferred(Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()))

	def __init__(self, id_booking, note, upd_datetime=datetime.now()):
		super().__init__()
		self.id_booking = id_booking
		self.note = note
		self.upd_datetime = upd_datetime

	def to_dict(self, exclude: Sequence[str] = None):
		_excluded = exclude or ('upd_datetime',)
		return super().to_dict(exclude=_excluded)

class UserNoteModel(Model, Base):
	"""
		UserNote Model
		ATTRIBUTES:
			id: Integer
			id_user: Integer
			note: Text
			upd_datetime: DateTime
	"""

	__tablename__ = 'user_notes'

	id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
	id_user = Column(Integer, ForeignKey('users.id', onupdate='CASCADE'), nullable=False)
	note = Column(Text, nullable=False)
	upd_datetime = deferred(Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()))

	def __init__(self, id_user, note, upd_datetime=datetime.now()):
		super().__init__()
		self.id_user = id_user
		self.note = note
		self.upd_datetime = upd_datetime

	def to_dict(self, exclude: Sequence[str] = None):
		_excluded = exclude or ('upd_datetime',)
		return super().to_dict(exclude=_excluded)
