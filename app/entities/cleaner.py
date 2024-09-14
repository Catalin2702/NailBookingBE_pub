from datetime import datetime, timedelta
from sqlalchemy import and_

from app.entities.entity import Entity
from utils.constants import EnumMailStates
from utils.exceptions import exception
from utils.tools import response
from utils.messages import generic_error


class CleanerEntity(Entity):
	def __init__(self):
		super().__init__()

	@exception(generic_error)
	def clean_actions(self, expired_days=30):
		with self.get_session() as session:
			expired_datetime = datetime.now() - timedelta(days=expired_days)
			session.query(self.Action).filter(self.Action.upd_datetime <= expired_datetime).delete()
		return response(True)

	@exception(generic_error)
	def clean_mails(self, expired_days=30):
		with (self.get_session() as session):
			expired_datetime = datetime.now() - timedelta(days=expired_days)
			id_mails: list[tuple[int]] = session.query(
				self.Mail.id
			).outerjoin(
				self.Confirmation, self.Mail.id == self.Confirmation.id_mail
			).outerjoin(
				self.Action, self.Mail.id == self.Action.id_mail
			).filter(
				and_(
					self.Mail.upd_datetime <= expired_datetime,
					self.Mail.status == EnumMailStates.COMPLETE,
					self.Confirmation.id_mail.is_(None),
					self.Action.id_mail.is_(None)
				)
			).all()
			session.query(self.Mail).filter(self.Mail.id.in_([id_mail[0] for id_mail in id_mails])).delete()
		return response(True)

	@exception(generic_error)
	def clean_confirmations(self, expired_days=30):
		with self.get_session() as session:
			expired_datetime = datetime.now() - timedelta(days=expired_days)
			session.query(self.Confirmation).filter(self.Confirmation.upd_datetime <= expired_datetime).delete()
		return response(True)

	@classmethod
	@exception(generic_error)
	def clean_errors(cls, expired_days=30):
		with cls.get_session() as session:
			expired_datetime = datetime.now() - timedelta(days=expired_days)
			session.query(cls.Error).filter(cls.Error.upd_datetime <= expired_datetime).delete()
		return response(True)

	@classmethod
	@exception(generic_error)
	def clean_sessions(cls, expired_days=30):
		with cls.get_session() as session:
			expired_datetime = datetime.now() - timedelta(days=expired_days)
			session.query(cls.SessionUser).filter(
				and_(
					cls.SessionUser.valid == False,
					cls.SessionUser.upd_datetime <= expired_datetime
				)
			).delete()
		return response(True)
