from sqlalchemy import Column, String, Date, ForeignKey, DateTime, Integer, DECIMAL, Boolean, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import deferred
from typing import Sequence

from app.models.base import Model, Base
from utils.constants import ConstRoles
from utils.env import ParamsEnv


class RoleModel(Model, Base, ConstRoles):
	"""
		Role Model
		ATTRIBUTES:
			role: String(20)
			description: String(255)
		METHODS:
			__init__: init
	"""

	__tablename__ = 'roles'

	role = Column(Integer, primary_key=True, nullable=False)
	description = deferred(Column(String(255), nullable=False))

	def __init__(self, role, description = None):
		super().__init__()
		self.role = role
		self.description = description


class UserModel(Model, Base):
	"""
		User Model
		ATTRIBUTES:
			id: Integer
			email: String(255)
			password: String(255)
			role: Integer
			phone: String(20)
			name: String(255)
			surname: String(255)
			birthday: Date
			instagram: String(64)
			valid: Boolean
			upd_datetime: DateTime
		METHODS:
			__init__: init
	"""

	__tablename__ = 'users'

	id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
	email = Column(String(255), nullable=False, unique=True, index=True)
	password = deferred(Column(String(64), nullable=True))
	role = Column(Integer, ForeignKey('roles.role'), default=ConstRoles.GUEST, index=True)
	phone = Column(String(20), nullable=True)
	name = Column(String(255), nullable=True, index=True)
	surname = Column(String(255), nullable=True, index=True)
	birthday = Column(Date, nullable=True)
	instagram = Column(String(64), nullable=True)
	valid = deferred(Column(Boolean, nullable=False, default=False))
	upd_datetime = deferred(Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()))

	def __init__(self, email: str, role: int, password: str = None, phone: str = None, name: str = None, surname: str = None, birthday: str = None, instagram: str = None, valid = False, upd_datetime = func.now()):
		super().__init__()
		self.email = email
		self.password = password
		self.role = role
		self.phone = phone
		self.name = name
		self.surname = surname
		self.birthday = birthday
		self.instagram = instagram
		self.valid = valid
		self.upd_datetime = upd_datetime

	def to_dict(self, exclude: Sequence[str] = None) -> dict:
		"""
			Return a dict from a result object.
			:param exclude: Sequence[str]
			:return: dict
		"""
		_excluded = exclude or ('password', 'valid', 'upd_datetime')
		return super().to_dict(exclude=_excluded)


class SessionUserModel(Model, Base):
	"""
		Session Model
		ATTRIBUTES:
			id: Integer
			id_user: Integer
			uuid: String(36)
			valid: BOOLEAN
		METHODS:
			__init__: init
	"""

	__tablename__ = 'sessions'

	id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
	id_user = Column(Integer, ForeignKey('users.id'), nullable=False)
	uuid = Column(String(36), nullable=False, unique=True)
	valid = Column(Boolean, nullable=False, default=True)
	upd_datetime = deferred(Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()))

	def __init__(self, id_user: int, uuid: str, valid = True, upd_datetime = func.now()):
		super().__init__()
		self.id_user = id_user
		self.uuid = uuid
		self.valid = valid
		self.upd_datetime = upd_datetime


class TempUser:
	"""
		Temporary User Model
		ATTRIBUTES:
			role: Integer
	"""
	id = -1
	email = ''
	password = ''
	role = ConstRoles.GUEST
	phone = ''
	name = ''
	surname = ''
	birthday = ''
	instagram = ''
	valid = False
	upd_datetime = func.now()

	def __init__(self):
		self.id = -1
		self.email = ''
		self.password = ''
		self.role = ConstRoles.GUEST
		self.phone = ''
		self.name = ''
		self.surname = ''
		self.birthday = ''
		self.instagram = ''
		self.valid = False
		self.upd_datetime = func.now()

	def to_dict(self, exclude: Sequence[str] = None) -> dict:
		"""
			Return a dict from a result object.
			:param exclude: Sequence[str]
			:return: dict
		"""
		_excluded = exclude or ('password', 'valid', 'upd_datetime')
		return {key: value for key, value in self.__dict__.items() if not key.startswith('_') and key not in _excluded and not callable(value)}


class CouponModel(Model, Base):
	"""
		Coupon Model
		ATTRIBUTES:
			id: Integer
			id_user: Integer
			discount: DECIMAL(10, 2, unsigned=True)
			count: Integer
		METHODS:
			__init__: init
			get_by_user: get by user
			generate: generate
			increase: increase
	"""

	__tablename__ = 'coupons'
	__table_args__ = (
		CheckConstraint('count >= 0 and count <= 8'),
	)

	id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
	id_user = Column(Integer, ForeignKey('users.id'), nullable=True)
	discount = Column(DECIMAL(10, 2), nullable=False)
	count = Column(Integer, nullable=False)
	upd_datetime = deferred(Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()))

	def __init__(self, id_user: int, discount: float, count: int):
		super().__init__()
		self.id_user = id_user
		self.discount = discount
		self.count = count

	@classmethod
	def get_by_user(cls, user: UserModel) -> 'CouponModel':
		_coupon = super().get(cls.id_user == user.id)
		if not _coupon:
			return cls.generate(user)
		return _coupon

	@classmethod
	def generate(cls, user: UserModel) -> 'CouponModel':
		_min = list(ParamsEnv.CATALOG.DISCOUNT.values())[0]
		with cls.get_session() as session:
			_coupon = cls(user.id, _min, 0)
			session.add(_coupon)
			session.flush()
			session.refresh(_coupon)
		return _coupon

	def increase(self) -> 'CouponModel':
		with self.get_session() as session:
			_coupon: 'CouponModel' = session.query(CouponModel).filter(CouponModel.id == self.id).first()
			if not _coupon:
				return _coupon

			_coupon.count += 1
			if _coupon.count > 8:
				_coupon.count = 1

			_values = list(ParamsEnv.CATALOG.DISCOUNT.values())
			_min, _max = _values[0], _values[1]

			_coupon.discount = _min if 1 <= _coupon.count <= 4 else _max
		return _coupon

	def to_dict(self, exclude: Sequence[str] = None) -> dict:
		_excluded = exclude or ('upd_datetime',)
		return super().to_dict(exclude=_excluded)
