from sqlalchemy import and_
from json import loads

from app.entities.entity import Entity
from utils.constants import EnumActionType
from utils.exceptions import exception
from utils.tools import response, Parameter
from utils.messages import generic_error, Messages, Errors


class ActionEntity(Entity):

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	@classmethod
	@exception(generic_error)
	def confirm_email(cls, action_code: str) -> dict:
		"""
			Confirm mail
			:param action_code: str
			:return: dict
		"""
		with cls.get_session() as session:
			action: cls.Action = session.query(cls.Action).filter(
				and_(
					cls.Action.code == action_code,
					cls.Action.type == EnumActionType.CONFIRM_EMAIL,
				)
			).first()

			if not action:
				return response(True, Errors.INVALID_CONFIRM_EMAIL)

			try:
				_id_user: int = Parameter('id_user', loads(action.params), int, True).value
			except ValueError as e:
				return response(True, f'{Errors.INVALID_CONFIRM_EMAIL}. {str(e)}')
			
			account: cls.User = session.query(cls.User).filter(cls.User.id == _id_user).first()
			if not account:
				return response(True, Errors.INVALID_USER)

			account.valid = True
			session.delete(action)

		return response(True, Messages.EMAIL_CONFIRMED)

	@classmethod
	@exception(generic_error)
	def confirm_join_account(cls, action_code: str) -> dict:
		"""
			Confirm join account
			:param action_code: str
			:return: dict
		"""
		with cls.get_session() as session:
			action: cls.Action = session.query(cls.Action).filter(
				and_(
					cls.Action.code == action_code,
					cls.Action.type == EnumActionType.JOIN_ACCOUNT,
				)
			).first()

			if not action:
				return response(True, Errors.INVALID_JOIN_ACCOUNT)

			try:
				_params = loads(action.params)
				_id_user: int = Parameter('id_user', _params, int, True).value
				_instagram: str = Parameter('instagram', _params, str, False).value
				_password: str = Parameter('password', _params, str, True).value
				del _params
			except ValueError as e:
				return response(True, f'{Errors.INVALID_JOIN_ACCOUNT}. {str(e)}')

			account: cls.User = session.query(cls.User).filter(cls.User.id == _id_user).first()
			if not account:
				return response(True, Errors.INVALID_USER)

			account.role = cls.Role.USER
			account.instagram = _instagram or account.instagram
			account.valid = True
			account.password = _password

			sessions: list[cls.SessionUser] = session.query(cls.SessionUser).filter(
				and_(
					cls.SessionUser.id_user == account.id,
					cls.SessionUser.valid == True,
				)
			).all()
			for s in sessions:
				s.valid = False

			session.delete(action)

		return response(True, Messages.JOIN_ACCOUNT)
