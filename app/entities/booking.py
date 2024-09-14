from datetime import datetime, time, date
from itertools import groupby
from json import dumps, loads
from sqlalchemy import and_, or_, cast, String, case
from typing import Union

from app.entities.entity import Entity
from app.services.account import AccountService
from app.services.context import Context
from utils.constants import EnumBookingStates, EnumMailTypes, EnumConfirmationType, EnumActionType, EnumMailStates
from utils.env import EmailEnv
from utils.exceptions import exception
from utils.tools import response, Parameter
from utils.messages import Errors, Messages, generic_error


class BookingEntity(Entity):

	def __init__(self, **kwargs):
		kwargs['mapping'] = {
			'getCalendarData': self.get_calendar,
			'bookBooking': self.book_booking,
			'getBookingEntity': self.get_booking_entity,
			'getBooking': self.get_booking,
			'getBookingInternalData': self.get_booking_internal_data,
			'getAllBookingData': self.get_all_booking_data,
			'getBookings': self.get_bookings,
			'cancelBooking': self.cancel_booking,
			'deleteBooking': self.delete_booking,
			'createBooking': self.create_booking,
			'requestBooking': self.request_booking,
			'editBooking': self.edit_booking,
			'editBookingInternalData': self.edit_booking_internal_data,
			'acceptBooking': self.accept_booking,
			'confirmBooking': self.confirm_booking,
		}
		super().__init__(**kwargs)

	@classmethod
	@exception(generic_error)
	async def get_calendar(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Get booking
			:param kwargs: dict
			:return: dict
		"""
		try:
			_month: int = Parameter('month', kwargs, int, True).value
			_year: int = Parameter('year', kwargs, int, True).value
			_identifier: str = Parameter('identifier', kwargs, str, True).value
		except ValueError as e:
			return response(False, f'{Errors.GET_CALENDAR}. {str(e)}')
		del kwargs

		if _identifier not in Context:
			return response(False, Errors.PERMISSION_DENIED)

		if not _month or not _year:
			return response(False, Errors.GENERIC_ERROR)

		today: date = datetime.today().date()
		user: cls.User = Context[_identifier]

		expr = [cast(cls.Booking.date, String).like(f"{_year}-{_month:02}-%")]
		order_by = (
			cls.Booking.date,
			case(
				(cls.Booking.status == str(EnumBookingStates.FREE), 1),
				(cls.Booking.status == str(EnumBookingStates.PENDING), 2),
				(cls.Booking.status == str(EnumBookingStates.BOOKED), 3),
				(cls.Booking.status == str(EnumBookingStates.CONFIRMED), 4),
				(cls.Booking.status == str(EnumBookingStates.COMPLETED), 5),
				(cls.Booking.status == str(EnumBookingStates.CANCELLED), 6),
				(cls.Booking.status == str(EnumBookingStates.PAUSED), 7),
				else_=8
			),
			cls.Booking.start,
		)

		match user.role:
			case cls.Role.ADMIN:
				pass
			case cls.Role.GUEST:
				expr.extend(
					[
						cls.Booking.date >= today,
						cls.Booking.status == EnumBookingStates.FREE,
						cls.Booking.id_user.is_(None),
					]
				)
			case _:
				expr.append(
					or_(
						and_(
							cls.Booking.date >= today,
							cls.Booking.status == EnumBookingStates.FREE,
							cls.Booking.id_user.is_(None),
						),
						cls.Booking.id_user == user.id
					)
				)

		with cls.get_session(commit=False) as session:
			bookings: list[cls.Booking] = session.query(cls.Booking).filter(and_(*expr)).order_by(*order_by).all()

		excluded = ('date', 'id_user', 'note', 'id_request', 'upd_datetime', 'upd_user')
		_now = datetime.now()
		content = {
			_date.strftime('%Y%m%d'): [
				{
					**booking.to_dict(excluded),
					'editable': booking.is_editable(user, _now),
					'other': booking.is_other(user),
				} for booking in g_booking
			] for _date, g_booking in groupby(bookings, key=lambda x: x.date)
		}

		return response(True, '', content)

	@classmethod
	@exception(generic_error)
	async def book_booking(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Set booking
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
			_id: int = Parameter('id', kwargs, int, True).value
			_note: str = Parameter('note', kwargs, str, False).value
		except ValueError as e:
			return response(False, f'{Errors.BOOK_BOOKING}. {str(e)}')

		if _identifier not in Context:
			return response(False, Errors.LOGIN)

		new_anon = {}
		user: cls.User = Context[_identifier]

		if user.role == cls.Role.GUEST:
			new_anon = await AccountService.register(**kwargs)
			if not new_anon['status']:
				return new_anon
			user: cls.User = Context[_identifier]

		del kwargs

		with cls.get_session() as session:
			booking: cls.Booking = session.query(cls.Booking).filter(cls.Booking.id == _id).first()
			if not booking:
				return response(False, Errors.NO_BOOKING)
			if booking.status == EnumBookingStates.FREE:
				booking.status = EnumBookingStates.PENDING
				booking.note = _note
				booking.id_user = user.id
				booking.upd_user = user.id

				book_booking = cls.Confirmation(
					_type=EnumConfirmationType.ACCEPT_BOOKING,
					id_booking=booking.id,
				)
				session.add(book_booking)

				confirm_booking = cls.Confirmation(
					_type=EnumConfirmationType.CONFIRM_BOOKING,
					id_booking=booking.id,
				)
				session.add(confirm_booking)
			else:
				return response(False, Errors.BOOKED)

		params = booking.to_dict()

		cls.generate_email(
			booking,
			Messages.MAIL_BOOKING,
			params,
			EnumMailTypes.BOOK_BOOKING,
			user,
		)

		email = user.email if new_anon else ''
		uuid = new_anon['content']['uuid'] if new_anon else ''

		return response(True, Messages.BOOKED, {
			'email': email,
			'uuid': uuid,
		})

	@classmethod
	def get_booking_entity(cls, id_booking) -> Entity.Booking:
		"""
			Get Booking entity
			:param id_booking: int
			:return: Booked
		"""
		return cls.Booking.get(cls.Booking.id == id_booking)

	@classmethod
	@exception(generic_error)
	async def get_booking(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Get Bookings
			:param kwargs: dict
			:return: dict
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
			_id: int = Parameter('id', kwargs, int, True).value
		except ValueError as e:
			return response(False, f'{Errors.GET_BOOKING}. {str(e)}')
		del kwargs

		if _identifier not in Context:
			return response(False, Errors.PERMISSION_DENIED)

		user: cls.User = Context[_identifier]

		with (cls.get_session(commit=False) as session):
			expr = (cls.Booking.id == _id,)
			if user.role != cls.Role.ADMIN:
				expr += (
					or_(
						cls.Booking.id_user == user.id,
						cls.Booking.id_user.is_(None),
						cls.Booking.status != EnumBookingStates.PAUSED,
					),
				)

			booking: cls.Booking = session.query(cls.Booking).filter(and_(*expr)).first()

			if booking:
				if booking.id_user:
					customer: cls.User = session.query(cls.User).filter(cls.User.id == int(booking.id_user)).first()
				else:
					customer = cls.TempUser()

				user_exclude = ('id', 'password', 'valid', 'upd_datetime')
				_now = datetime.now()

				return response(True, '', {
					'booking': {
						**booking.to_dict(),
						**customer.to_dict(user_exclude),
						'editable': booking.is_editable(user, _now),
						'other': booking.is_other(user),
						'acceptable': booking.is_acceptable(user),
						'confirmable': booking.is_confirmable(user),
						'disposable': booking.is_disposable(user),
						'erasable': booking.is_erasable(user),
					}
				})
			else:
				return response(False, Errors.NO_BOOKING)

	@classmethod
	@exception(generic_error)
	async def get_booking_internal_data(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Get Booking Internal Data
			:param kwargs: dict
			:return: dict
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
			_id: int = Parameter('id', kwargs, int, True).value
		except ValueError as e:
			return response(False, f'{Errors.GET_BOOKING_INTERNAL_DATA}. {str(e)}')
		del kwargs

		if _identifier not in Context or Context[_identifier].role != cls.Role.ADMIN:
			return response(False, Errors.PERMISSION_DENIED)

		internal_note: cls.BookingNote = cls.BookingNote.get(cls.BookingNote.id_booking == _id)

		return response(True, '', {'internalNote': internal_note.note if internal_note else ''})

	@classmethod
	@exception(generic_error)
	async def get_all_booking_data(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Get All Booking Data
			:param kwargs: dict
			:return: dict
		"""

		booking_dict = await cls.get_booking(**kwargs)
		if not booking_dict['status']:
			return booking_dict

		internal_note = await cls.get_booking_internal_data(**kwargs)
		if not internal_note['status']:
			return internal_note

		booking_dict['content']['booking']['internalNote'] = internal_note['content']['internalNote']

		return booking_dict

	@classmethod
	@exception(generic_error)
	async def get_bookings(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Get Bookings
			:param kwargs: dict
			:return: dict
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
			_year: int = Parameter('y', kwargs, int, True).value
			_month: int = Parameter('m', kwargs, int, True).value
			_day: int = Parameter('d', kwargs, int, True).value
		except ValueError as e:
			return response(False, f'{Errors.GET_BOOKINGS}. {str(e)}')
		del kwargs

		if _identifier not in Context or Context[_identifier].role != cls.Role.ADMIN:
			return response(False, Errors.PERMISSION_DENIED)

		user: cls.User = Context[_identifier]

		with cls.get_session(commit=False) as session:
			bookings: list[cls.Booking] = session.query(cls.Booking).filter(
				and_(cast(cls.Booking.date, String) == f'{_year}-{_month:02}-{_day:02}')
			).all()

			if not bookings:
				return response(True, Errors.NO_BOOKING, {'bookings': []})

			customers: list[cls.User] = session.query(cls.User).filter(cls.User.id.in_(
				set(res.id_user for res in bookings)
			)).all()

		user_exclude = ('id', 'password', 'valid', 'upd_datetime')
		_now = datetime.now()

		result = tuple(
			{
				**booking.to_dict(),
				**(next((customer.to_dict(user_exclude) for customer in customers if customer.id == booking.id_user), {})),
				'editable': booking.is_editable(user, _now),
				'other': booking.is_other(user),
				'acceptable': booking.is_acceptable(user),
				'confirmable': booking.is_confirmable(user),
				'disposable': booking.is_disposable(user),
				'erasable': booking.is_erasable(user),
			} for booking in bookings
		)

		return response(True, '', {'bookings': result})

	@classmethod
	@exception(generic_error)
	async def cancel_booking(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Cancel Booking
			:param kwargs: dict
			:return: dict
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
			_id: int = Parameter('id', kwargs, int, True).value
		except ValueError as e:
			return response(False, f'{Errors.CANCEL}. {str(e)}')
		del kwargs

		if _identifier not in Context:
			return response(False, Errors.PERMISSION_DENIED)

		user: cls.User = Context[_identifier]

		with cls.get_session() as session:
			if user.role == cls.Role.ADMIN:
				expr = (cls.Booking.id == _id,)
			else:
				expr = (cls.Booking.id == _id, cls.Booking.id_user == user.id)

			booking: cls.Booking = session.query(cls.Booking).filter(and_(*expr)).first()

			if not booking:
				return response(False, Errors.NO_BOOKING)
			if booking.status == EnumBookingStates.CANCELLED:
				return response(False, Errors.ALREADY_CANCELED)
			if booking.status == EnumBookingStates.COMPLETED:
				return response(False, Errors.CANCEL_ALREADY_COMPLETED)

			params_before = booking.to_dict()

			booking.status = EnumBookingStates.CANCELLED
			booking.upd_user = user.id

			params_after = booking.to_dict()

			session.query(cls.Confirmation).filter(cls.Confirmation.id_booking == int(booking.id)).delete(synchronize_session=False)

			if user.role != cls.Role.ADMIN:
				params = dumps(params_after, default=str)
				session.add(
					cls.Action(
						_type=EnumActionType.NEW_BOOKING,
						params=params,
					)
				)

			if user.id == booking.id_user:
				customer: cls.User = session.query(cls.User).filter(cls.User.email == str(EmailEnv.INFO.EMAIL)).first()
			elif booking.id_user:
				customer: cls.User = session.query(cls.User).filter(cls.User.id == int(booking.id_user)).first()
			else:
				return response(True, Messages.CANCEL)

			params_after.update(customer.to_dict())

		cls.generate_email(
			booking,
			Messages.MAIL_CANCEL.format(name=customer.name, surname=customer.surname),
			[params_before, params_after],
			EnumMailTypes.CANCEL
		)

		return response(True, Messages.CANCEL)

	@classmethod
	@exception(generic_error)
	async def create_booking(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Create Booking
			:param kwargs: dict
			:return: dict
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
			_date: date = Parameter('date', kwargs, date, True, format_='%Y-%m-%d').value
			_start: time = Parameter('start', kwargs, time, True, format_='%H:%M').value
			_end: time = Parameter('end', kwargs, time, True, format_='%H:%M').value
		except ValueError as e:
			return response(False, f'{Errors.NEW_BOOKING}. {str(e)}')
		del kwargs

		if _identifier not in Context or Context[_identifier].role != cls.Role.ADMIN:
			return response(False, Errors.PERMISSION_DENIED)

		user: cls.User = Context[_identifier]

		with cls.get_session() as session:
			session.add(
				cls.Booking(
					date=_date,
					start=_start,
					end=_end,
					upd_user=user.id,
				)
			)

		return response(True, Messages.NEW_BOOKING)

	@classmethod
	@exception(generic_error)
	async def request_booking(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Request Booking
			:param kwargs: dict
			:return: dict
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
			_date: date = Parameter('date', kwargs, date, True, format_='%Y-%m-%d').value
			_start: time = Parameter('start', kwargs, time, True, format_='%H:%M').value
			_end: time = Parameter('end', kwargs, time, True, format_='%H:%M').value
			_note: str = Parameter('note', kwargs, str, False).value
		except ValueError as e:
			return response(False, f'{Errors.REQUEST_NEW_BOOKING}. {str(e)}')
		del kwargs

		if _identifier not in Context or Context[_identifier].role not in (cls.Role.ADMIN, cls.Role.USER):
			return response(False, Errors.PERMISSION_DENIED)

		user: cls.User = Context[_identifier]
		params = {
			'date': _date,
			'start': _start,
			'end': _end,
			'note': _note,
			'status': EnumBookingStates.BOOKED,
			'client': {**user.to_dict()},
		}

		with cls.get_session() as session:
			session.add(
				cls.Action(
					_type=EnumActionType.REQUEST_NEW_BOOKING,
					params=dumps(params, default=str),
				)
			)

		return response(True, Messages.SENDED_NEW_REQUEST_BOOKING)

	@classmethod
	@exception(generic_error)
	async def edit_booking(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Edit Booked
			:param kwargs: dict
			:return: dict
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
			_id: int = Parameter('id', kwargs, int, True).value
			_date: date = Parameter('date', kwargs, date, False, format_='%Y-%m-%d').value
			_start: time = Parameter('start', kwargs, time, False, format_='%H:%M').value
			_end: time = Parameter('end', kwargs, time, False, format_='%H:%M').value
			_status: str = Parameter('status', kwargs, str, False).value
			_note: str = Parameter('note', kwargs, str, False).value
			_internal_note: str = Parameter('internalNote', kwargs, str, False).value
		except ValueError as e:
			return response(False, f'{Errors.EDIT_BOOKING}. {str(e)}')
		del kwargs

		if _identifier not in Context:
			return response(False, Errors.PERMISSION_DENIED)

		if _internal_note:
			res = await cls.edit_booking_internal_data(identifier=_identifier, id=_id, internalNote=_internal_note)
			if not res['status']:
				return res

		user: cls.User = Context[_identifier]

		if (_start or _end or _status or _date) and not user.role == cls.Role.ADMIN:
			return response(False, Errors.PERMISSION_DENIED)

		send_mail = True

		with cls.get_session() as session:
			booking: cls.Booking = session.query(cls.Booking).filter(cls.Booking.id == _id).first()
			if not booking:
				return response(False, Errors.NO_BOOKING)

			params_before: dict = booking.to_dict()
			if user.role == cls.Role.ADMIN:
				booking.start = _start or booking.start
				booking.end = _end or booking.end
				booking.note = _note or booking.note
				booking.date = _date or booking.date
				booking.upd_user = user.id
				booking.status = _status or booking.status

				if not booking.id_user:
					send_mail = False

				if booking.status == EnumBookingStates.COMPLETED:
					send_mail = False
					if booking.id_user:
						customer: cls.User = session.query(cls.User).filter(cls.User.id == int(booking.id_user)).first()
						coupon = cls.Coupon.get_by_user(customer)
						if coupon:
							coupon.increase()

			else:
				if user.id != booking.id_user:
					return response(False, Errors.PERMISSION_DENIED)
				booking.note = _note or booking.note

			booking.upd_user = user.id

			if send_mail:
				if user.id == booking.id_user:
					customer: cls.User = session.query(cls.User).filter(cls.User.email == str(EmailEnv.INFO.EMAIL)).first()
				else:
					customer: cls.User = session.query(cls.User).filter(cls.User.id == int(booking.id_user)).first()

				if customer:
					params_after = {
						**booking.to_dict(),
						**customer.to_dict(),
					}
				else:
					params_after = booking.to_dict()

				cls.generate_email(
					booking,
					Messages.MAIL_UPDATE.format(name=customer.name, surname=customer.surname),
					[params_before, params_after],
					EnumMailTypes.UPDATE,
				)

		return response(True, Messages.EDIT_BOOKING)

	@classmethod
	@exception(generic_error)
	async def edit_booking_internal_data(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Edit Booking Internal Data
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
			_id: int = Parameter('id', kwargs, int, True).value
			_internal_note: str = Parameter('internalNote', kwargs, str, True).value
		except ValueError as e:
			return response(False, f'{Errors.EDIT_BOOKING_INTERNAL_DATA}. {str(e)}')
		del kwargs

		if _identifier not in Context or Context[_identifier].role != cls.Role.ADMIN:
			return response(False, Errors.PERMISSION_DENIED)

		with cls.get_session() as session:
			booking_note: cls.BookingNote = session.query(cls.BookingNote).filter(cls.BookingNote.id_booking == _id).first()
			if booking_note:
				booking_note.note = _internal_note
			else:
				booking_note = cls.BookingNote(
					id_booking=_id,
					note=_internal_note,
				)
				session.add(booking_note)

		return response(True, Messages.EDIT_BOOKING_INTERNAL_DATA)

	@classmethod
	@exception(generic_error)
	async def delete_booking(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Delete Booking
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
			_id: int = Parameter('id', kwargs, int, True).value
		except ValueError as e:
			return response(False, f'{Errors.DELETE_BOOKING}. {str(e)}')
		del kwargs

		if _identifier not in Context or Context[_identifier].role != cls.Role.ADMIN:
			return response(False, Errors.PERMISSION_DENIED)

		with cls.get_session() as session:
			session.query(cls.Confirmation).filter(cls.Confirmation.id_booking == _id).delete(synchronize_session=False)
			session.query(cls.BookingNote).filter(cls.BookingNote.id_booking == _id).delete(synchronize_session=False)
			session.delete(session.query(cls.Booking).filter(cls.Booking.id == _id).first())  # write like this to trigger the SQLAlchemy event

		return response(True, Messages.DELETE)

	@classmethod
	@exception(generic_error)
	async def accept_booking(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Accept Booking
			:param kwargs: dict
			:return: dict
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
			_id: int = Parameter('id', kwargs, int, True).value
		except ValueError as e:
			return response(False, f'{Errors.ACCEPT_BOOKING}. {str(e)}')
		del kwargs

		if _identifier not in Context or Context[_identifier].role != cls.Role.ADMIN:
			return response(False, Errors.PERMISSION_DENIED)

		user: cls.User = Context[_identifier]

		with cls.get_session() as session:
			booking: cls.Booking = session.query(cls.Booking).filter(cls.Booking.id == _id).first()
			if not booking:
				return response(False, Errors.NO_BOOKING)

			if booking.status == EnumBookingStates.CONFIRMED:
				return response(False, Errors.ALREADY_CONFIRMED)
			elif booking.status != EnumBookingStates.PENDING:
				return response(False, Errors.ACCEPT_BOOKING_NOT_PENDING)

			params_before = booking.to_dict()
			booking.status = EnumBookingStates.BOOKED
			booking.upd_user = user.id

			confirmations: list[cls.Confirmation] = session.query(cls.Confirmation).filter(
				and_(
					cls.Confirmation.id_booking == booking.id,
					cls.Confirmation.type == EnumConfirmationType.ACCEPT_BOOKING
				)
			).all()

			mails: list[cls.Mail] = session.query(cls.Mail).filter(
				and_(
					cls.Mail.status != EnumMailStates.COMPLETE,
					cls.Mail.id.in_(set(confirm.id_mail for confirm in confirmations))
				)
			).all()

			session.query(cls.Confirmation).filter(cls.Confirmation.id.in_(set(confirm.id for confirm in confirmations))).delete(synchronize_session=False)
			session.query(cls.Mail).filter(cls.Mail.id.in_(set(mail.id for mail in mails))).delete(synchronize_session=False)

			if user.id == booking.id_user:
				customer: cls.User = session.query(cls.User).filter(cls.User.email == str(EmailEnv.INFO.EMAIL)).first()
			else:
				customer: cls.User = session.query(cls.User).filter(cls.User.id == int(booking.id_user)).first()

			params_after = {
				**booking.to_dict(),
				**customer.to_dict(),
			}

		cls.generate_email(
			booking,
			Messages.MAIL_UPDATE.format(name=customer.name, surname=customer.surname),
			[params_before, params_after],
			EnumMailTypes.UPDATE,
		)

		return response(True, Messages.ACCEPT_BOOKING)

	@classmethod
	@exception(generic_error)
	async def confirm_booking(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Confirm Booking
			:param kwargs: dict
			:return: dict
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
			_id: int = Parameter('id', kwargs, int, True).value
		except ValueError as e:
			return response(False, f'{Errors.ACCEPT_BOOKING}. {str(e)}')
		del kwargs

		send_mail = True

		if _identifier not in Context:
			return response(False, Errors.PERMISSION_DENIED)
		user: cls.User = Context[_identifier]

		with cls.get_session() as session:
			expr = (cls.Booking.id == _id,)
			if user.role != cls.Role.ADMIN:
				expr += (cls.Booking.id_user == user.id,)

			booking: cls.Booking = session.query(cls.Booking).filter(and_(*expr)).first()

			if not booking:
				return response(False, Errors.NO_BOOKING)

			match booking.status:
				case EnumBookingStates.CONFIRMED:
					return response(False, Errors.ALREADY_CONFIRMED)
				case EnumBookingStates.PENDING:
					return response(False, Errors.CONFIRM_BOOKING_NOT_BOOKED)

			params_before = booking.to_dict()
			booking.status = EnumBookingStates.CONFIRMED
			booking.upd_user = user.id

			session.query(cls.Confirmation).filter(
				and_(
					cls.Confirmation.id_booking == booking.id,
					cls.Confirmation.type == EnumConfirmationType.CONFIRM_BOOKING
				)
			).delete()

			if not booking.id_user:
				send_mail = False

			if send_mail:
				if user.id == booking.id_user:
					customer: cls.User = session.query(cls.User).filter(cls.User.email == str(EmailEnv.INFO.EMAIL)).first()
				else:
					customer: cls.User = session.query(cls.User).filter(cls.User.id == int(booking.id_user)).first()

				params_after = {
					**booking.to_dict(),
					**customer.to_dict(),
				}

		if send_mail:
			cls.generate_email(
				booking,
				Messages.MAIL_UPDATE.format(name=customer.name, surname=customer.surname),
				[params_before, params_after],
				EnumMailTypes.UPDATE,
			)
			cls.generate_email(
				booking,
				Messages.MAIL_RULES,
				params_after,
				EnumMailTypes.RULES,
				customer.email
			)
		return response(True, Messages.CONFIRM_BOOKING)

	@classmethod
	@exception(generic_error)
	def confirm_booking_by_code(cls, confirm_code: str) -> dict[str, Union[bool, str, dict]]:
		"""
			Confirm Booking using confirmation code
			:param confirm_code: str
			:return: dict
		"""
		with cls.get_session() as session:
			confirm: cls.Confirmation = session.query(cls.Confirmation).filter(
				and_(
					cls.Confirmation.type == EnumConfirmationType.CONFIRM_BOOKING,
					cls.Confirmation.code == confirm_code
				)
			).first()

			if not confirm:
				return response(False, Errors.INVALID_CONFIRMATION)

			booking: cls.Booking = session.query(cls.Booking).filter(and_(cls.Booking.id == confirm.id_booking)).first()
			params_before = booking.to_dict()

			if not booking:
				return response(False, Errors.NO_BOOKING)

			if booking.status == EnumBookingStates.CONFIRMED:
				return response(False, Errors.ALREADY_CONFIRMED)

			booking.status = EnumBookingStates.CONFIRMED
			booking.upd_user = booking.id_user

			session.delete(confirm)

			admin: cls.User = session.query(cls.User).filter(cls.User.email == str(EmailEnv.INFO.EMAIL)).first()
			customer: cls.User = session.query(cls.User).filter(cls.User.id == int(booking.id_user)).first()

			params_after_admin = {
				**booking.to_dict(),
				**admin.to_dict(),
			}
			params_after = {
				**booking.to_dict(),
				**customer.to_dict(),
			}

		cls.generate_email(
			booking,
			Messages.MAIL_UPDATE.format(name=customer.name, surname=customer.surname),
			[params_before, params_after_admin],
			EnumMailTypes.UPDATE,
			EmailEnv.INFO.EMAIL
		)
		cls.generate_email(
			booking,
			Messages.MAIL_RULES,
			params_after,
			EnumMailTypes.RULES,
			customer.email
		)
		return response(True, Messages.CONFIRM_BOOKING)

	@classmethod
	@exception(generic_error)
	def accept_booking_by_code(cls, booked_code: str) -> dict[str, Union[bool, str, dict]]:
		"""
			Booked Booking using booked code
			:param booked_code: str
			:return: dict
		"""
		with cls.get_session() as session:
			confirm: cls.Confirmation = session.query(cls.Confirmation).filter(
				and_(
					cls.Confirmation.type == EnumConfirmationType.ACCEPT_BOOKING,
					cls.Confirmation.code == booked_code
				)
			).first()

			if not confirm:
				return response(False, Errors.INVALID_CONFIRMATION)

			booking: cls.Booking = session.query(cls.Booking).filter(cls.Booking.id == int(confirm.id_booking)).first()
			params_before = booking.to_dict()

			if not booking:
				return response(False, Errors.NO_BOOKING)

			if booking.status == EnumBookingStates.BOOKED:
				return response(False, Errors.ALREADY_BOOKED)

			user: cls.User = session.query(cls.User).filter(cls.User.email == str(EmailEnv.INFO.EMAIL)).first()
			booking.status = EnumBookingStates.BOOKED
			booking.upd_user = user.id

			session.delete(confirm)

			customer: cls.User = session.query(cls.User).filter(cls.User.id == int(booking.id_user)).first()

			params_after = {
				**booking.to_dict(),
				**customer.to_dict(),
			}

		cls.generate_email(
			booking,
			Messages.MAIL_UPDATE.format(name=customer.name, surname=customer.surname),
			[params_before, params_after],
			EnumMailTypes.UPDATE,
		)
		return response(True, Messages.ACCEPT_BOOKING)

	@classmethod
	@exception(generic_error)
	def complete_bookings(cls) -> dict[str, Union[bool, str, dict]]:
		"""
			Complete Bookings
			:return: dict
		"""
		with cls.get_session() as session:
			now = datetime.now()
			bookings: list[cls.Booking] = session.query(cls.Booking).filter(
				and_(
					cls.Booking.status == EnumBookingStates.CONFIRMED,
					or_(
						cls.Booking.date < now.date(),
						and_(
							cls.Booking.date == now.date(),
							cls.Booking.end <= now.time()
						)
					)
				)
			).all()

			for booking in bookings:
				booking.status = EnumBookingStates.COMPLETED

				if booking.id_user:
					customer: cls.User = session.query(cls.User).filter(cls.User.id == int(booking.id_user)).first()
					coupon = cls.Coupon.get_by_user(customer)
					if coupon:
						coupon.increase()

		return response(True, Messages.COMPLETE_BOOKINGS)

	@classmethod
	@exception(generic_error)
	def generate_new_booking(cls, action_code: str) -> dict[str, Union[bool, str, dict]]:
		"""
			Generate new booking
			:param action_code: str
			:return: dict
		"""
		with cls.get_session() as session:
			action: cls.Action = session.query(cls.Action).filter(
				and_(
					cls.Action.code == action_code,
					cls.Action.type == EnumActionType.NEW_BOOKING,
				)
			).first()

			if not action:
				return response(True, Errors.INVALID_NEW_BOOKING)

			try:
				_params = loads(action.params)
				_date: date = Parameter('date', _params, date, True, format_='%Y-%m-%d').value
				_start: time = Parameter('start', _params, time, True, format_='%H:%M:%S').value
				_end: time = Parameter('end', _params, time, True, format_='%H:%M:%S').value
				del _params
			except ValueError as e:
				return response(False, f'{Errors.GENERATE_NEW_BOOKING}. {str(e)}')


			session.add(
				cls.Booking(
					date=_date,
					start=_start,
					end=_end,
				)
			)
			session.delete(action)

		return response(True, Messages.NEW_BOOKING)

	@classmethod
	@exception(generic_error)
	def request_new_booking(cls, action_code: str) -> dict[str, Union[bool, str, dict]]:
		"""
			Request new booking
			:param action_code: str
			:return: dict
		"""
		with cls.get_session() as session:
			action: cls.Action = session.query(cls.Action).filter(
				and_(
					cls.Action.code == action_code,
					cls.Action.type == EnumActionType.REQUEST_NEW_BOOKING,
				)
			).first()

			if not action:
				return response(True, Errors.INVALID_REQUEST_NEW_BOOKING)

			try:
				_action_params = loads(action.params)
				_date: date = Parameter('date', _action_params, date, True, format_='%Y-%m-%d').value
				_start: time = Parameter('start', _action_params, time, True, format_='%H:%M:%S').value
				_end: time = Parameter('end', _action_params, time, True, format_='%H:%M:%S').value
				_note: str = Parameter('note', _action_params, str, False).value
				_id_user: int = Parameter('id', _action_params['client'], int, True).value
				del _action_params
			except ValueError as e:
				return response(False, f'{Errors.REQUEST_NEW_BOOKING}. {str(e)}')


			booking: cls.Booking = cls.Booking(
				date=_date,
				start=_start,
				end=_end,
				id_user=_id_user,
				status=EnumBookingStates.BOOKED,
			)

			params = booking.to_dict()

			session.add(booking)
			session.delete(action)

			user: cls.User = session.query(cls.User).filter(cls.User.id == _id_user).first()

		cls.generate_email(
			booking,
			Messages.MAIL_BOOKING,
			params,
			EnumMailTypes.BOOK_BOOKING,
			user,
		)

		return response(True, Messages.REQUEST_NEW_BOOKING_SUCCESS)
