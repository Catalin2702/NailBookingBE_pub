from sqlalchemy import and_, cast
from sqlalchemy.dialects.postgresql import TIMESTAMP, INTERVAL
from datetime import datetime
from json import dumps, loads

from app.entities.entity import Entity
from utils.constants import EnumMailTypes, EnumBookingStates, EnumConfirmationType, EnumActionType
from utils.exceptions import exception
from utils.env import EmailEnv
from utils.tools import response
from utils.messages import generic_error, Errors, Messages


class MailEntity(Entity):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	@classmethod
	@exception(generic_error)
	def get_mails_to_send(cls) -> dict:
		"""
			Get all mails to send
			:return: dict
		"""
		mails: cls.Mail = cls.Mail.get_many(and_(
			cls.Mail.status.in_(['TO_SEND', 'ERROR']),
			cls.Mail.attempts <= EmailEnv.ATTEMPTS,
		))

		if not mails:
			return response(False, Errors.NO_MAIL, [])
		else:
			return response(True, '', mails)

	@classmethod
	@exception(generic_error)
	def get_mail_entity(cls, id_mail: int) -> Entity.Mail:
		"""
			Get a mail entity
			:param id_mail: int
			:return: Mail
		"""
		return cls.Mail.get(cls.Mail.id == id_mail)

	@classmethod
	@exception(generic_error)
	def generate_confirmed_mail(cls) -> dict:
		"""
			Generate confirm mail
			:return: dict
		"""
		with cls.get_session() as session:
			confirm_ids: list[cls.Confirmation.id] = session.query(
				cls.Confirmation.id
			).join(
				cls.Booking, and_(
					cls.Booking.id == cls.Confirmation.id_booking,
					cls.Booking.status == EnumBookingStates.BOOKED,
					cast(cls.Booking.date, TIMESTAMP) + cls.Booking.start - cast(f'{1} DAY', INTERVAL)
					<= datetime.now(),
				)
			).filter(
				and_(
					cls.Confirmation.type == EnumConfirmationType.CONFIRM_BOOKING,
					cls.Confirmation.id_mail.is_(None),
				)
			).all()

			if not confirm_ids:
				return response(True)

			confirm_bookings: list[cls.Confirmation] = session.query(cls.Confirmation).filter(
				cls.Confirmation.id.in_([c.id for c in confirm_ids])
			).all()

			bookings: list[cls.Booking] = session.query(cls.Booking).filter(
				cls.Booking.id.in_([r.id_booking for r in confirm_bookings])
			).all()

			users: list[cls.User] = session.query(cls.User).filter(
				cls.User.id.in_(set([r.id_user for r in bookings]))
			).all()

			params = {}

			for booking in bookings:
				_user = next((u for u in users if u.id == booking.id_user), None)
				if not _user:
					continue

				params.update(
					{
						'code': str(next((c.code for c in confirm_bookings if c.id_booking == booking.id), None)),
						**booking.to_dict(),
						**_user.to_dict()
					}
				)

				mail = cls.Mail(
					receiver=_user.email,
					subject=Messages.MAIL_CONFIRM + Messages.MAIL_TIME.format(date=booking.date.strftime('%d-%m-%Y'), start=f'{booking.start.hour:02}:{booking.start.minute:02}'),
					params=dumps(params, default=str),
					_type=EnumMailTypes.CONFIRM_BOOKING,
				)
				session.add(mail)
				session.flush()
				session.refresh(mail)

				_confirm_booking = next((c for c in confirm_bookings if c.id_booking == booking.id), None)
				_confirm_booking.id_mail = mail.id

		return response(True)

	@classmethod
	@exception(generic_error)
	def generate_booked_mail(cls) -> dict:
		"""
			Generate booked mail
			:return: dict
		"""
		with cls.get_session() as session:
			booked_bookings: list[cls.Confirmation] = session.query(cls.Confirmation).filter(
				and_(
					cls.Confirmation.type == EnumConfirmationType.ACCEPT_BOOKING,
					cls.Confirmation.id_mail.is_(None),
				)
			).all()

			if not booked_bookings:
				return response(True)

			bookings: list[cls.Booking] = session.query(cls.Booking).filter(
				cls.Booking.id.in_([b.id_booking for b in booked_bookings])
			).all()

			users: list[cls.User] = session.query(cls.User).filter(
				cls.User.id.in_(set([r.id_user for r in bookings]))
			).all()

			for res in bookings:
				_user: cls.User = next((u for u in users if u.id == res.id_user), None)
				params = {
						'client': _user.to_dict(),
						'code': str(next((c.code for c in booked_bookings if c.id_booking == res.id), None)),
						**cls.result_to_dict(res)
					}

				mail = cls.Mail(
					receiver=EmailEnv.INFO.EMAIL,
					subject=Messages.MAIL_BOOKING_REQUEST.format(
						name=_user.name,
						surname=_user.surname,
						date=res.date.strftime('%d-%m-%Y'),
						start=res.start.strftime('%H:%M'),
					),
					params=dumps(params, default=str),
					_type=EnumMailTypes.REQUEST_BOOKING,
				)
				session.add(mail)
				session.flush()
				session.refresh(mail)

				_book_booking = next((c for c in booked_bookings if c.id_booking == res.id), None)
				_book_booking.id_mail = mail.id

		return response(True)

	@classmethod
	@exception(generic_error)
	def generate_new_booking_mail(cls) -> dict:
		"""
			Generate new booking mail
			:return: dict
		"""
		with cls.get_session() as session:
			actions: list[cls.Action] = session.query(cls.Action).filter(
				and_(
					cls.Action.id_mail.is_(None),
					cls.Action.type == EnumActionType.NEW_BOOKING
				)
			).all()

			if not actions:
				return response(True)

			for action in actions:
				params = loads(action.params)
				subject = Messages.MAIL_GENERATE_NEW_BOOKING + Messages.MAIL_TIME.format(date=params['date'], start=params['start'][0:5])
				params['code'] = action.code
				mail = cls.Mail(
					receiver=EmailEnv.INFO.EMAIL,
					subject=subject,
					params=dumps(params),
					_type=EnumMailTypes.GENERATE_NEW_BOOKING,
				)
				session.add(mail)
				session.flush()
				session.refresh(mail)
				action.id_mail = mail.id

		return response(True)

	@classmethod
	@exception(generic_error)
	def generate_confirm_email_mail(cls) -> dict:
		"""
			Generate confirm email mail
			:return: dict
		"""
		with cls.get_session() as session:
			actions: list[cls.Action] = session.query(cls.Action).filter(
				and_(
					cls.Action.type == EnumActionType.CONFIRM_EMAIL,
					cls.Action.id_mail.is_(None),
				)
			).all()

			if not actions:
				return response(True)

			for action in actions:
				params = loads(action.params)
				params['code'] = action.code
				mail = cls.Mail(
					receiver=params['email'],
					subject=Messages.MAIL_CONFIRM_EMAIL,
					params=dumps(params),
					_type=EnumMailTypes.CONFIRM_EMAIL,
				)
				session.add(mail)
				session.flush()
				session.refresh(mail)
				action.id_mail = mail.id

		return response(True)

	@classmethod
	@exception(generic_error)
	def generate_join_account_mail(cls) -> dict:
		"""
			Generate join account mail
			:return: dict
		"""
		with cls.get_session() as session:
			actions: list[cls.Action] = session.query(cls.Action).filter(
				and_(
					cls.Action.type == EnumActionType.JOIN_ACCOUNT,
					cls.Action.id_mail.is_(None),
				)
			).all()

			if not actions:
				return response(True)

			for action in actions:
				params = loads(action.params)
				params['code'] = action.code
				mail = cls.Mail(
					receiver=params['email'],
					subject=Messages.MAIL_JOIN_ACCOUNT,
					params=dumps(params, default=str),
					_type=EnumMailTypes.JOIN_ACCOUNT,
				)
				session.add(mail)
				session.flush()
				session.refresh(mail)
				action.id_mail = mail.id

		return response(True)

	@classmethod
	@exception(generic_error)
	def generate_new_request_booking_mail(cls) -> dict:
		"""
			Generate new request booking mail
			:return: dict
		"""
		with cls.get_session() as session:
			actions: list[cls.Action] = session.query(cls.Action).filter(
				and_(
					cls.Action.type == EnumActionType.REQUEST_NEW_BOOKING,
					cls.Action.id_mail.is_(None),
				)
			).all()

			if not actions:
				return response(True)

			id_users = set([loads(action.params)['client']['id'] for action in actions])
			users: list[cls.User] = session.query(cls.User).filter(cls.User.id.in_(id_users)).all()

			for action in actions:
				params = loads(action.params)
				params['code'] = action.code

				_user = next((u for u in users if u.id == params['client']['id']), None)

				mail = cls.Mail(
					receiver=EmailEnv.INFO.EMAIL,
					subject=Messages.MAIL_NEW_BOOKING_REQUEST.format(
						**_user.to_dict(),
						date=params['date'],
						start=params['start'],
					),
					params=dumps(params, default=str),
					_type=EnumMailTypes.REQUEST_NEW_BOOKING,
				)
				session.add(mail)
				session.flush()
				session.refresh(mail)
				action.id_mail = mail.id

		return response(True)

	@classmethod
	@exception(generic_error)
	def generate_forgot_password_mail(cls) -> dict:
		"""
			Generate forgot password mail
			:return: dict
		"""
		with cls.get_session() as session:
			actions: list[cls.Action] = session.query(cls.Action).filter(
				and_(
					cls.Action.type == EnumActionType.FORGOT_PASSWORD,
					cls.Action.id_mail.is_(None),
				)
			).all()

			if not actions:
				return response(True)

			for action in actions:
				params = loads(action.params)
				email_params = {
					'client': {
						'name': params.get('name', ''),
					},
					'code': action.code,
				}
				mail = cls.Mail(
						receiver=params['email'],
						subject=Messages.MAIL_FORGOT_PASSWORD,
						params=dumps(email_params),
						_type=EnumMailTypes.FORGOT_PASSWORD,
					)
				session.add(mail)
				session.flush()
				session.refresh(mail)
				action.id_mail = mail.id

		return response(True)
