from datetime import date
from hashlib import sha256
from json import dumps, loads
from sqlalchemy import and_, or_
from typing import Union
from uuid import uuid4

from app.entities.entity import Entity
from app.services.context import Context
from utils.constants import EnumActionType
from utils.tools import response, Parameter
from utils.messages import Errors, Messages
from utils.exceptions import exception


class AccountEntity(Entity):

	def __init__(self, **kwargs):
		kwargs['mapping'] = {
			'login': self.login,
			'guestLogin': self.guest_login,
			'logout': self.logout,
			'register': self.register,
			'delete': self.delete,
			'userData': self.user_data,
			'update': self.update,
			'forgotPassword': self.forgot_password,
			'restorePassword': self.restore_password,
		}
		super().__init__(**kwargs)

	@classmethod
	@exception(response(False, Errors.LOGIN))
	async def login(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Login user
			:param kwargs: {email: str, password: str, uuid: str}
			:return: {status: str, message: str, content: dict}
		"""
		try:
			_email: str = Parameter('email', kwargs, str, True).value
			_password: str = Parameter('password', kwargs, str, False).value
			_uuid: str = Parameter('uuid', kwargs, str, False).value
		except ValueError as e:
			return response(False, f'{Errors.LOGIN}. {str(e)}')
		del kwargs

		if _email and (_password or _uuid):
			status = True
			message = ''
			session_user = None
			with cls.get_session() as session:
				if _password:
					user: cls.User = session.query(cls.User).filter(
						and_(
							cls.User.email == _email,
							cls.User.password == sha256(_password.encode()).hexdigest()
						)
					).first()
					if not user:
						status = False
						message = Errors.EMAIL_PASSWORD
						user: cls.TempUser = cls.TempUser()
					else:
						session_user = session.query(cls.SessionUser).filter(
							and_(
								cls.SessionUser.id_user == user.id,
								cls.SessionUser.valid == True,
							)
						).order_by(cls.SessionUser.id.desc()).first()

						message = Messages.LOGIN

				else:
					user: cls.User = session.query(cls.User).filter(cls.User.email == _email).first()
					if not user:
						user: cls.TempUser = cls.TempUser()
					else:
						session_user = session.query(cls.SessionUser).filter(
							and_(
								cls.SessionUser.id_user == user.id,
								cls.SessionUser.uuid == _uuid,
								cls.SessionUser.valid == True,
							)
						).order_by(cls.SessionUser.id.desc()).first()
				if not session_user and not isinstance(user, cls.TempUser):
					session_user = cls.SessionUser(
						id_user=user.id,
						uuid=uuid4(),
						valid=True,
					)
					session.add(session_user)
					session.flush()
					session.refresh(session_user)

			return response(status, message, {
				**user.to_dict(),
				'identifier': Context.add_user(user),
				'uuid': session_user.uuid if session_user else '',
			})
		else:
			return await cls.guest_login()

	@classmethod
	@exception(response(False, Errors.LOGIN))
	async def guest_login(cls, **_) -> dict[str, Union[bool, str, dict]]:
		"""
			Login user as guest
		"""
		del _
		user: cls.TempUser = cls.TempUser()
		identifier = str(uuid4())
		while identifier in Context:
			identifier = str(uuid4())
		Context[identifier] = user

		return response(True, '', {
			**user.to_dict(),
			'identifier': identifier,
			'uuid': '',
		})


	@classmethod
	@exception(response(False, Errors.LOGOUT))
	async def logout(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Logout user
			:param kwargs: {identifier: str, uuid: str}
			:return: {status: str, message: str, content: dict}
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
			_uuid: str = Parameter('uuid', kwargs, str, True).value
		except ValueError as e:
			return response(False, f'{Errors.LOGOUT}. {str(e)}')
		del kwargs

		if not _identifier in Context:
			return response(False, f'{Errors.NOT_FOUND}. {Errors.PERMISSION_DENIED}')
		else:
			user: cls.User = Context[_identifier]
			if user.role != cls.Role.GUEST:
				with cls.get_session() as session:
					session_user = session.query(cls.SessionUser).filter(
						and_(
							cls.SessionUser.id_user == user.id,
							cls.SessionUser.uuid == _uuid,
							cls.SessionUser.valid == True,
						)
					).order_by(cls.SessionUser.id.desc()).first()
					if session_user:
						session.delete(session_user)

		del Context[_identifier]
		return response(True, Messages.LOGOUT)

	@classmethod
	@exception(response(False, Errors.REGISTER))
	async def register(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Register user
			:param kwargs: dict
			:return: dict
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
			_name: str = Parameter('name', kwargs, str, True).value
			_surname: str = Parameter('surname', kwargs, str, True).value
			_email: str = Parameter('email', kwargs, str, True).value
			_birthday: date = Parameter('birthday', kwargs, date, True, format_='%Y-%m-%d').value
			_phone: str = Parameter('phone', kwargs, str, True).value
			_instagram: str = Parameter('instagram', kwargs, str, False).value
			_password: str = Parameter('password', kwargs, str, False).value
			_confirm_password: str = Parameter('confirmPassword', kwargs, str, False).value
		except ValueError as e:
			return response(False, f'{Errors.REGISTER}. {str(e)}')
		del kwargs

		if _identifier not in Context:
			return response(False, f'{Errors.REGISTER}. {Errors.PERMISSION_DENIED}')

		with cls.get_session() as session:
			e_user: cls.User = session.query(cls.User).filter(cls.User.email == _email).first()
			if e_user:
				if e_user.role == cls.Role.ANON:
					if e_user.name == _name and e_user.surname == _surname and e_user.birthday == _birthday and e_user.phone == _phone:
						if _password and _password == _confirm_password:
							params = dumps(
								{
									'id_user': e_user.id,
									'name': _name,
									'surname': _surname,
									'email': _email,
									'phone': _phone,
									'birthday': _birthday,
									'instagram': _instagram,
									'password': sha256(_password.encode()).hexdigest()
								},
								default=str
							)
							join_account = cls.Action(
								_type=EnumActionType.JOIN_ACCOUNT,
								params=params,
							)
							session.add(join_account)
							return response(True, '.'.join((Messages.REQUEST_JOIN_ACCOUNT, Messages.SENDING_CONFIRM_MAIL)))
						else:
							return response(False, Errors.DIFFERENT_PASSWORDS)
					else:
						return response(False, Errors.EMAIL_EXISTS)
				else:
					return response(False, Errors.EMAIL_EXISTS)
			else:
				if not _password:
					new_user = cls.User(
						name=_name,
						surname=_surname,
						email=_email,
						phone=_phone,
						birthday=_birthday,
						instagram=_instagram,
						role=cls.Role.ANON,
					)
					session.add(new_user)
					session.flush()
					session.refresh(new_user)
					Context[_identifier] = new_user

				elif _password == _confirm_password:
					new_user = cls.User(
						name=_name,
						surname=_surname,
						email=_email,
						password=sha256(_password.encode()).hexdigest(),
						phone=_phone,
						birthday=_birthday,
						instagram=_instagram,
						role=cls.Role.USER,
					)
					session.add(new_user)
					session.flush()
					session.refresh(new_user)
					Context[_identifier] = new_user

				else:
					return response(False, Errors.DIFFERENT_PASSWORDS)

				params = dumps(
					{
						'id_user': new_user.id,
						'name': _name,
						'surname': _surname,
						'email': _email,
						'phone': _phone,
						'birthday': _birthday,
						'instagram': _instagram,
					},
					default=str
				)
				confirm_mail = cls.Action(
					_type=EnumActionType.CONFIRM_EMAIL,
					params=params,
				)
				session.add(confirm_mail)

			user: cls.User = Context[_identifier]
			session.query(cls.SessionUser).filter(
				and_(
					cls.SessionUser.id_user == user.id,
					cls.SessionUser.valid == True
				)
			).update({'valid': False})
			new_session_user = cls.SessionUser(
				id_user=user.id,
				uuid=uuid4(),
			)
			session.add(new_session_user)
			session.flush()
			session.refresh(new_session_user)

		return response(True, '.'.join((Messages.REGISTER, Messages.SENDING_CONFIRM_MAIL)), {
			'email': _email,
			'uuid': new_session_user.uuid,
		})

	@classmethod
	@exception(response(False, Errors.DELETE))
	async def delete(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Delete user
			:param kwargs: {identifier: str, uuid: str}
			:return: {status: str, message: str, content: dict}
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
		except ValueError as e:
			return response(False, f'{Errors.DELETE}. {str(e)}')
		del kwargs

		if not _identifier in Context:
			return response(False, f'{Errors.DELETE}. {Errors.PERMISSION_DENIED}')
		else:
			user: cls.User = Context[_identifier]
			if user.role != cls.Role.GUEST:
				with cls.get_session() as session:
					bookings: list[cls.Booking] = session.query(cls.Booking).filter(
						or_(
							cls.Booking.id_user == user.id,
							cls.Booking.upd_user == user.id,
						)
					).all()
					for booking in bookings:
						if booking.id_user == user.id:
							booking.id_user = None
						if booking.upd_user == user.id:
							booking.upd_user = None

					session.query(cls.Confirmation).filter(cls.Confirmation.id_booking.in_([booking.id for booking in bookings])).delete()
					session.query(cls.SessionUser).filter(cls.SessionUser.id_user == int(user.id)).delete()
					session.query(cls.UserNote).filter(cls.UserNote.id_user == int(user.id)).delete()
					session.query(cls.User).filter(cls.User.id == int(user.id)).delete()

		del Context[_identifier]
		return response(True, Messages.DELETE)

	@classmethod
	@exception(response(False, Errors.USER_DATA))
	async def user_data(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Get user data
			:param kwargs: {identifier: str}
			:return: {status: str, message: str, content: dict}
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
		except ValueError as e:
			return response(False, f'{Errors.USER_DATA}. {str(e)}')
		del kwargs

		if not _identifier in Context:
			return response(False, Errors.USER_DATA,)
		user: cls.User = Context[_identifier]
		with cls.get_session(commit=False) as session:
			session_user: cls.SessionUser = session.query(cls.SessionUser).filter(
				and_(
					cls.SessionUser.id_user == user.id,
					cls.SessionUser.valid == True,
				)).order_by(cls.SessionUser.id.desc()).first()

			if not session_user:
				session.rollback()
				return response(False, Errors.SESSION)

		return response(True, '', {
			**user.to_dict(),
			'identifier': _identifier,
			'uuid': session_user.uuid,
		})

	@classmethod
	@exception(response(False, Errors.UPDATE))
	async def update(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Update user data
			:param kwargs: {name: str, surname: str, email: str, phone: str, birthday: str, instagram: str, identifier: str, password: str, confirmPassword: str}
			:return: {status: str, message: str, content: dict}
		"""
		try:
			_identifier: str = Parameter('identifier', kwargs, str, True).value
			_name: str = Parameter('name', kwargs, str, False).value
			_surname: str = Parameter('surname', kwargs, str, False).value
			_email: str = Parameter('email', kwargs, str, False).value
			_phone: str = Parameter('phone', kwargs, str, False).value
			_birthday: date = Parameter('birthday', kwargs, date, False, format_='%Y-%m-%d').value
			_instagram: str = Parameter('instagram', kwargs, str, False).value
			_password: str = Parameter('password', kwargs, str, False).value
			_confirm_password: str = Parameter('confirmPassword', kwargs, str, False).value
		except ValueError as e:
			return response(False, f'{Errors.UPDATE}. {str(e)}')
		del kwargs

		if _identifier not in Context:
			return response(False, f'{Errors.UPDATE}. {Errors.PERMISSION_DENIED}')
		user: cls.User = Context[_identifier]

		with cls.get_session() as session:
			user: cls.User = session.query(cls.User).filter(cls.User.id == int(user.id)).first()
			if not user:
				return response(False, Errors.NOT_FOUND)

			if _password == _confirm_password != '':
				user.name = _name or user.name
				user.surname = _surname or user.surname
				user.email = _email or user.email
				user.phone = _phone or user.phone
				user.birthday = _birthday or user.birthday
				user.instagram = _instagram or user.instagram
				user.password = sha256(_password.encode()).hexdigest()

				session_user: cls.SessionUser = session.query(cls.SessionUser).filter(cls.SessionUser.id_user == int(user.id)).all()
				for su in session_user:
					su.valid = False
				session_user = cls.SessionUser(
					id_user=user.id,
					uuid=uuid4(),
					valid=True,
				)
				session.add(session_user)

			elif _password != _confirm_password:
				return response(False, Errors.DIFFERENT_PASSWORDS)

			else:
				user.name = _name or user.name
				user.surname = _surname or user.surname
				user.email = _email or user.email
				user.phone = _phone or user.phone
				user.birthday = _birthday or user.birthday
				user.instagram = _instagram or user.instagram

				session_user: cls.SessionUser = session.query(cls.SessionUser).filter(
					and_(
						cls.SessionUser.id_user == user.id,
						cls.SessionUser.valid == True,
					)).order_by(cls.SessionUser.id.desc()).first()
				if not session_user:
					session.rollback()
					return response(False, Errors.SESSION)

		Context[_identifier] = user

		return response(True, Messages.UPDATE, {
			'name': user.name,
			'surname': user.surname,
			'email': user.email,
			'phone': user.phone,
			'birthday': user.birthday,
			'instagram': user.instagram,
			'role': user.role,
			'identifier': _identifier,
			'uuid': session_user.uuid,
		})

	@classmethod
	def get_user(cls, id_user: int) -> Entity.User:
		return cls.User.get(cls.User.id == id_user)

	@classmethod
	@exception(response(False, Errors.FORGOT_PASSWORD))
	async def forgot_password(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Forgot password
			:param kwargs: {email: str}
			:return: {status: str, message: str, content: dict}
		"""
		try:
			_email: str = Parameter('email', kwargs, str, True).value
		except ValueError as e:
			return response(False, f'{Errors.FORGOT_PASSWORD}. {str(e)}')
		del kwargs

		with cls.get_session() as session:
			user: cls.User = session.query(cls.User).filter(cls.User.email == _email).first()
			if not user:
				return response(True, Messages.FORGOT_PASSWORD)

			session.add(
				cls.Action(
					_type=EnumActionType.FORGOT_PASSWORD,
					params=dumps(user.to_dict(), default=str),
				)
			)

		return response(True, Messages.FORGOT_PASSWORD)

	@classmethod
	@exception(response(False, Errors.RESTORE_PASSWORD))
	async def restore_password(cls, **kwargs) -> dict[str, Union[bool, str, dict]]:
		"""
			Restore password
			:param kwargs: {code: str, password: str, confirmPassword: str}
			:return: {status: str, message: str, content: dict}
		"""
		try:
			_code: str = Parameter('code', kwargs, str, True).value
			_new_password: str = Parameter('newPassword', kwargs, str, True).value
			_confirm_password: str = Parameter('confirmPassword', kwargs, str, True).value
		except ValueError as e:
			return response(False, f'{Errors.RESTORE_PASSWORD}. {str(e)}')
		del kwargs

		if _new_password != _confirm_password:
			return response(False, Errors.DIFFERENT_PASSWORDS)

		if len(_new_password) < 8:
			return response(False, Errors.PASSWORD_LENGTH)

		with cls.get_session() as session:
			action: cls.Action = session.query(cls.Action).filter(
				and_(
					cls.Action.code == _code,
					cls.Action.type == EnumActionType.FORGOT_PASSWORD,
				)
			).first()
			if not action:
				return response(False, Errors.INVALID_RESTORE_PASSWORD)

			try:
				_id_user: int = Parameter('id', loads(action.params), int, True).value
			except ValueError as e:
				return response(False, f'{Errors.INVALID_RESTORE_PASSWORD}. {str(e)}')

			user: cls.User = session.query(cls.User).filter(cls.User.id == _id_user).first()
			if not user:
				return response(False, Errors.INVALID_USER)

			user.password = sha256(_new_password.encode()).hexdigest()
			if user.role == cls.Role.ANON:
				user.role = cls.Role.USER

			session.delete(action)
			session.query(cls.SessionUser).filter(cls.SessionUser.id_user == int(user.id)).update({'valid': False})

		return response(True, Messages.RESTORE_PASSWORD)
