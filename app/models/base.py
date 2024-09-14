from contextlib import contextmanager
from sqlalchemy import create_engine, Engine, NullPool
from sqlalchemy.orm import declarative_base, sessionmaker, DeclarativeBase
from sqlalchemy.orm.session import Session
from typing import Sequence

from app.models.utils import _repr
from utils.env import DatabaseEnv


Base: DeclarativeBase = declarative_base()


class SessionModel:
	"""
		Base Session
		ATTRIBUTES:
			engine: Engine
	"""
	engine: Engine = create_engine(f'{DatabaseEnv.DIALECT}://{DatabaseEnv.USER}:{DatabaseEnv.PASS}@{DatabaseEnv.HOST}:{DatabaseEnv.PORT}/{DatabaseEnv.NAME}', poolclass=NullPool)
	Base.metadata.create_all(engine)

	@staticmethod
	@contextmanager
	def get_session(commit=True) -> Session:
		session = sessionmaker(bind=SessionModel.engine, expire_on_commit=False)()
		try:
			yield session
			if commit:
				session.commit()
		except Exception:
			session.rollback()
			raise
		finally:
			session.close()


class Model(SessionModel):
	"""
		Base Model
		ATTRIBUTES:
			engine: Engine
		METHODS:
			get_all: get all models
			get: get models by expression
			set: add entity to session
	"""

	@classmethod
	def __repr__(cls) -> str:
		return _repr(cls)

	@classmethod
	def __str__(cls) -> str:
		return _repr(cls)

	@classmethod
	def get_all(cls) -> list['Model']:
		"""
			Get all models
			:return: models
		"""
		with cls.get_session(commit=False) as session:
			return session.query(cls).all()

	@classmethod
	def get(cls, expr):
		"""
			Get entity by expression
			:param expr: expression

			:return: Model
		"""
		with cls.get_session(commit=False) as session:
			return session.query(cls).filter(expr).first()

	@classmethod
	def get_many(cls, expr, order_by=None) -> list['Model']:
		"""
			Get models by expression
			:param expr: expression
			:param order_by: order by
			:return: models
		"""
		with cls.get_session(commit=False) as session:
			if order_by:
				return session.query(cls).filter(expr).order_by(*order_by).all()
			return session.query(cls).filter(expr).all()

	def save(self):
		"""
			Add entity to session
		"""
		with self.get_session() as session:
			session.add(self)

	def to_dict(self, exclude: Sequence[str] = None) -> dict:
		"""
			Return a dict from a result object.
			:param exclude: Sequence[str]
			:return: dict
		"""
		return {key: value for key, value in self.__dict__.items() if not key.startswith('_') and key not in exclude and not callable(value)}
