from json import dumps
from sqlalchemy import Column, Text, DateTime, Enum, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.orm import deferred

from app.models.base import Model, Base
from app.models.user import UserModel
from utils.constants import EnumMailStates, EnumMailTypes


class MailModel(Model, Base, EnumMailStates, EnumMailTypes):
	"""
		Mail Model
		Attributes:
			id: Integer
			receiver: String
			subject: String
			params: Text
			type: String
			status: Enum(EnumMailStates)
			attempts: Integer
			upd_datetime: DateTime
		Methods:
			set_completed(cls, _id)
			set_error(self)
			create_mail(to, subject: str, params: dict, _type: str, sending_datetime=None)
	"""

	__tablename__ = 'mails'

	id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
	receiver = Column(String(255), nullable=False)
	subject = Column(String(255), nullable=False)
	params = Column(Text, nullable=False)
	sending_datetime = deferred(Column(DateTime, nullable=True, default=None))
	type = Column(String(20), nullable=False)
	status = Column(Enum(*EnumMailStates.values, name=EnumMailStates.name), nullable=False, default=EnumMailStates.TO_SEND)
	attempts = Column(Integer, nullable=False, default=0)
	upd_datetime = deferred(Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now()))

	def __init__(self, receiver, subject, params, _type, sending_datetime=None, status=EnumMailStates.TO_SEND, attempts=0, update_time=func.now()):
		super().__init__()
		self.receiver = receiver
		self.subject = subject
		self.params = params
		self.type = _type
		self.sending_datetime = sending_datetime
		self.status = status
		self.attempts = attempts
		self.upd_datetime = update_time

	@classmethod
	def set_completed(cls, _id):
		if isinstance(_id, int):
			_id = [_id]
		with cls.get_session() as session:
			mails: list[cls] = session.query(cls).filter(cls.id.in_(_id)).all()
			for mail in mails:
				mail.status = cls.COMPLETE

	def set_error(self):
		with self.get_session():
			self.attempts += 1
			self.status = self.ERROR

	@staticmethod
	def create_mail(to, subject: str, params: dict, _type: str, sending_datetime=None):
		if isinstance(to, UserModel):
			receiver = to.email
			params['name'] = to.name
		else:
			receiver = to

		MailModel(
			receiver=receiver,
			subject=subject,
			params=dumps(params, default=str),
			_type=_type,
			sending_datetime=sending_datetime
		).save()
