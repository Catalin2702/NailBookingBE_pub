from datetime import datetime, timedelta
from sqlalchemy import Column, Date, ForeignKey, Text, DateTime, Time, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.orm import deferred
from typing import Sequence

from app.models.base import Model, Base
from utils.constants import EnumBookingStates, ConstRoles


class BookingModel(Model, Base):
	"""
		Booking Model
		ATTRIBUTES:
			id: Integer
			date: Date
			start: Time
			end: Time
			id_user: Integer
			note: Text
			id_request: Integer
			status: String(20)
			upd_datetime: DateTime(timezone=True)
			upd_user: Integer
	"""

	__tablename__ = 'booking'

	id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
	date = Column(Date, nullable=False)
	start = Column(Time, nullable=False)
	end = Column(Time, nullable=False)
	id_user = Column(Integer, ForeignKey('users.id', onupdate='CASCADE'), nullable=True)
	note = Column(Text, nullable=True)
	id_request = deferred(Column(Integer, ForeignKey('requests.id', onupdate='CASCADE'), nullable=True))
	status = Column(String(20), nullable=False, default=EnumBookingStates.FREE)
	upd_datetime = deferred(Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()))
	upd_user = Column(Integer, ForeignKey('users.id', onupdate='CASCADE'), nullable=True)

	def __init__(self, date, start, end, id_user=None, note=None, id_request=None, status=EnumBookingStates.FREE, upd_datetime=func.now(), upd_user=None):
		super().__init__()
		self.date = date
		self.start = start
		self.end = end
		self.id_user = id_user
		self.note = note
		self.id_request = id_request
		self.status = status
		self.upd_datetime = upd_datetime
		self.upd_user = upd_user

	@property
	def month(self) -> int:
		return self.date.month

	@property
	def year(self) -> int:
		return self.date.year

	@property
	def day(self) -> int:
		return self.date.day

	@property
	def start_hour(self) -> int:
		return self.start.hour

	@property
	def start_minute(self) -> int:
		return self.start.minute

	def to_dict(self, exclude: Sequence[str] = None) -> dict:
		"""
			Return a dict from a result object.
			:param exclude: Sequence[str]
			:return: dict
		"""
		_excluded = exclude or ('upd_datetime', 'id_user', 'id_request', 'upd_user')
		return super().to_dict(exclude=_excluded)

	def is_editable(self, user, now=datetime.now()) -> bool:
		if user.role == ConstRoles.ADMIN:
			return True
		return (
			(self.date > now.date() or self.date == now.date() and self.start >= now.time()) and
			self.status not in (EnumBookingStates.CANCELLED, EnumBookingStates.CONFIRMED, EnumBookingStates.FREE) and
			self.id_user and self.id_user == user.id
		)

	def is_acceptable(self, user) -> bool:
		return self.status == EnumBookingStates.PENDING and user.role == ConstRoles.ADMIN

	def is_confirmable(self, user, now=datetime.now()) -> bool:
		if user.role == ConstRoles.ADMIN:
			return self.status == EnumBookingStates.BOOKED
		return (
			self.id_user and self.id_user == user.id and self.status == EnumBookingStates.BOOKED and
			datetime.combine(self.date, self.start) - timedelta(days=1) <= now
		)

	def is_disposable(self, user) -> bool:
		return user.role == ConstRoles.ADMIN and self.status in (EnumBookingStates.FREE, EnumBookingStates.CANCELLED)

	def is_erasable(self, user) -> bool:
		if self.status not in (EnumBookingStates.PENDING, EnumBookingStates.BOOKED, EnumBookingStates.CONFIRMED):
			return False
		if user.role == ConstRoles.ADMIN:
			return True
		return self.id_user == user.id

	def is_other(self, user) -> bool:
		return user.role == ConstRoles.ADMIN and self.id_user and self.id_user != user.id
