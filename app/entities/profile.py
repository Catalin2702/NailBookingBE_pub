from datetime import datetime, date

from sqlalchemy import and_, case

from app.services.booking import BookingService
from app.entities.entity import Entity
from app.services.context import Context
from utils.messages import Errors, generic_error, Messages
from utils.exceptions import exception
from utils.constants import EnumBookingStates
from utils.tools import response, Parameter


class ProfileEntity(Entity):

	def __init__(self, **kwargs):
		kwargs['mapping'] = {
			'getCoupon': self.get_coupon_data,
			'getRecapBookings': self.get_recap_bookings,
			'cancelBooking': BookingService.cancel_booking,
			'getBooking': BookingService.get_booking,
			'getBookingInternalData': BookingService.get_booking_internal_data,
			'getAllBookingData': BookingService.get_all_booking_data,
			'editBooking': BookingService.edit_booking,
			'editBookingInternalData': BookingService.edit_booking_internal_data,
			'getUsersBookings': self.get_users_bookings,
			'getUser': self.get_user,
			'getUsers': self.get_users,
			'getUserDetails': self.get_user_details,
			'editUser': self.edit_user,
		}
		super().__init__(**kwargs)

	@classmethod
	@exception(generic_error)
	async def get_coupon_data(cls, **kwargs) -> dict[str, str | dict[str, int]]:
		"""
			Get Coupon
			:param kwargs: dict
			:return: dict
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
		except ValueError as e:
			return response(False, str(e))
		del kwargs

		if not _identifier in Context or Context[_identifier].role not in (cls.Role.USER, cls.Role.ADMIN):
			return response(False, Errors.PERMISSION_DENIED)

		coupon: cls.Coupon = cls.Coupon.get_by_user(Context[_identifier])
		_exclude = ('id', 'id_user', 'upd_datetime')

		return response(True, '', {'coupon': coupon.to_dict(_exclude)})

	@classmethod
	@exception(generic_error)
	async def get_recap_bookings(cls, **kwargs) -> dict:
		"""
			Get All Bookings
			:param kwargs: dict
			:return: dict
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
			_active: bool = Parameter('active', kwargs, bool, False).value
		except ValueError as e:
			return response(False, str(e))
		del kwargs

		if not _identifier in Context:
			return response(False, Errors.PERMISSION_DENIED)

		user: cls.User = Context[_identifier]
		today = datetime.now().date()

		expr = [cls.Booking.id_user == user.id]
		if _active:
			expr.extend(
				[
					cls.Booking.status != EnumBookingStates.CANCELLED,
					cls.Booking.date >= today,
					]
			)
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

		with cls.get_session(commit=False) as session:

			booking_customers: list[tuple[cls.Booking, cls.User]] = (
				session.query(cls.Booking, cls.User)
				.outerjoin(cls.User, cls.Booking.id_user == cls.User.id)
				.filter(and_(*expr))
				.order_by(*order_by)
				.all()
			)

		user_exclude = ('id', 'password', 'valid', 'upd_datetime')
		_now = datetime.now()

		return response(True, '', {
			'bookings': tuple(
				{
					**booking.to_dict(),
					**(customer.to_dict(user_exclude) if customer else {}),
					'other': booking.is_other(user),
					'acceptable': booking.is_acceptable(user),
					'erasable': booking.is_erasable(user),
					'disposable': booking.is_disposable(user),
					'editable': booking.is_editable(user, _now),
					'confirmable': booking.is_confirmable(user),
				} for booking, customer in booking_customers
			)
		})

	@classmethod
	@exception(generic_error)
	async def get_users_bookings(cls, **kwargs) -> dict:
		"""
			Get All Bookings
			:param kwargs: dict
			:return: dict
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
			_date_from: date = Parameter('date_from', kwargs, date, True, format_='%Y-%m-%d').value
			_date_to: date = Parameter('date_to', kwargs, date, True, format_='%Y-%m-%d').value
			_status: str = Parameter('status', kwargs, str, True).value
			_name: str = Parameter('name', kwargs, str, False).value
			_surname: str = Parameter('surname', kwargs, str, False).value
		except ValueError as e:
			return response(False, str(e))
		del kwargs

		if not _identifier in Context or Context[_identifier].role != cls.Role.ADMIN:
			return response(True, Errors.PERMISSION_DENIED)
		user: cls.User = Context[_identifier]

		expr = [
			cls.Booking.date >= _date_from,
			cls.Booking.date <= _date_to,
		]

		if _status != 'all':
			expr.append(cls.Booking.status == _status)

		if _name:
			expr.append(cls.User.name.ilike(f'%{_name}%'))

		if _surname:
			expr.append(cls.User.surname.ilike(f'%{_surname}%'))

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

		with cls.get_session(commit=False) as session:
			booking_customers: list[tuple[cls.Booking, cls.User]] = (
				session.query(cls.Booking, cls.User)
				.outerjoin(cls.User, cls.Booking.id_user == cls.User.id)
				.filter(and_(*expr))
				.order_by(*order_by)
				.all()
			)

		booking_exclude = ('upd_datetime', 'id_user', 'id_request', 'upd_user', 'note')
		user_exclude = ('id', 'password', 'valid', 'upd_datetime', 'birthday', 'instagram', 'role', 'phone', 'email')
		_now = datetime.now()
		return response(True, '', {
			'bookings': tuple(
				{
					**booking.to_dict(booking_exclude),
					**(customer.to_dict(user_exclude) if customer else {}),
					'other': booking.is_other(user),
					'acceptable': booking.is_acceptable(user),
					'erasable': booking.is_erasable(user),
					'disposable': booking.is_disposable(user),
					'editable': booking.is_editable(user, _now),
					'confirmable': booking.is_confirmable(user),
				} for booking, customer in booking_customers
			)
		})

	@classmethod
	@exception(generic_error)
	async def get_user(cls, **kwargs) -> dict:
		"""
			Get User
			:param kwargs: dict
			:return: dict
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
			_id: int = Parameter('id', kwargs, int, True).value
		except ValueError as e:
			return response(False, str(e))
		del kwargs

		if not _identifier in Context or Context[_identifier].role != cls.Role.ADMIN:
			return response(True, Errors.PERMISSION_DENIED)

		user: cls.User = cls.User.get(cls.User.id == _id)

		return response(True, '', {'user': user.to_dict()})

	@classmethod
	@exception(generic_error)
	async def get_users(cls, **kwargs) -> dict:
		"""
			Get Users
			:param kwargs
			:return: dict
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
			_name: str = Parameter('name', kwargs, str, False).value
			_surname: str = Parameter('surname', kwargs, str, False).value
			_email: str = Parameter('email', kwargs, str, False).value
			_phone: str = Parameter('phone', kwargs, str, False).value
			_instagram: str = Parameter('instagram', kwargs, str, False).value
		except ValueError as e:
			return response(False, str(e))
		del kwargs

		if not _identifier in Context or Context[_identifier].role != cls.Role.ADMIN:
			return response(True, Errors.PERMISSION_DENIED)

		expr = []

		if _name:
			expr.append(cls.User.name.ilike(f'%{_name}%'))

		if _surname:
			expr.append(cls.User.surname.ilike(f'%{_surname}%'))

		if _email:
			expr.append(cls.User.email.ilike(f'%{_email}%'))

		if _phone:
			expr.append(cls.User.phone.ilike(f'%{_phone}%'))

		if _instagram:
			expr.append(cls.User.instagram.ilike(f'%{_instagram}%'))

		order_by = [cls.User.name, cls.User.surname]

		users: list[cls.User] = cls.User.get_many(and_(*expr), order_by=order_by)

		exclude_user = ('email', 'password', 'role', 'phone', 'birthday', 'instagram', 'valid', 'upd_datetime')

		return response(True, '', {
			'users': tuple(user.to_dict(exclude_user) for user in users)
		})

	@classmethod
	@exception(generic_error)
	async def get_user_details(cls, **kwargs) -> dict:
		"""
			Get User Details
			:param kwargs
			:return: dict
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
			_id: int = Parameter('id', kwargs, int, True).value
		except ValueError as e:
			return response(False, str(e))
		del kwargs

		if not _identifier in Context or Context[_identifier].role not in (cls.Role.USER, cls.Role.ADMIN):
			return response(True, Errors.PERMISSION_DENIED)

		with cls.get_session(commit=False) as session:
			customer: cls.User = session.query(cls.User).filter(cls.User.id == int(_id)).first()
			if not customer:
				return response(False, Errors.NO_USER)
			user_note: cls.UserNote = session.query(cls.UserNote).filter(cls.UserNote.id_user == int(customer.id)).first()
		coupon: cls.Coupon = cls.Coupon.get_by_user(customer)

		_exclude = ('id', 'id_user', 'upd_datetime')

		user_details = {
			**customer.to_dict(),
			'coupon': coupon.to_dict(_exclude),
			'internalNote': user_note.note if user_note else '',
		}

		return response(True, '', {'user': user_details})

	@classmethod
	@exception(generic_error)
	async def edit_user(cls, **kwargs) -> dict:
		"""
			Edit User
			:param kwargs: dict
			:return: dict
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
			_id: int = Parameter('id', kwargs, int, True).value
			_name: str = Parameter('name', kwargs, str, False).value
			_surname: str = Parameter('surname', kwargs, str, False).value
			_email: str = Parameter('email', kwargs, str, False).value
			_phone: str = Parameter('phone', kwargs, str, False).value
			_birthday: date = Parameter('birthday', kwargs, date, False).value
			_instagram: str = Parameter('instagram', kwargs, str, False).value
			_role: int = Parameter('role', kwargs, int, False).value
			_count: int = Parameter('count', kwargs, int, False, default_=0, check_={'func': lambda x: 0 <= x <= 8, 'error': Errors.INVALID_COUPON_COUNT}).value
			_discount: float = Parameter('discount', kwargs, float, False).value
			_internalNote: str = Parameter('internalNote', kwargs, str, False).value
		except ValueError as e:
			return response(False, str(e))
		
		del kwargs

		if _identifier not in Context or Context[_identifier].role != cls.Role.ADMIN:
			return response(False, Errors.PERMISSION_DENIED)

		with cls.get_session() as session:
			customer: cls.User = session.query(cls.User).filter(cls.User.id == _id).first()
			if not customer:
				return response(False, Errors.NO_USER)

			customer.name = _name or customer.name
			customer.surname = _surname or customer.surname
			customer.email = _email or customer.email
			customer.phone = _phone or customer.phone
			customer.birthday = _birthday or customer.birthday
			customer.instagram = _instagram or customer.instagram
			customer.role = _role or customer.role

			if _count or _discount:
				coupon: cls.Coupon = session.query(cls.Coupon).filter(cls.Coupon.id_user == int(customer.id)).first()
				if not coupon:
					return response(False, Errors.NO_COUPON)

				coupon.count = _count or coupon.count
				coupon.discount = _discount or coupon.discount

			if _internalNote:
				note: cls.UserNote = session.query(cls.UserNote).filter(cls.UserNote.id_user == int(customer.id)).first()
				if not note:
					note = cls.UserNote(
						id_user=customer.id,
						note=_internalNote
					)
					session.add(note)
					session.flush()
					session.refresh(note)
				else:
					note.note = _internalNote

		return response(True, Messages.UPDATE_USER)
