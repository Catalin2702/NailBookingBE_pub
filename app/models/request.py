from sqlalchemy import Column, String, ForeignKey, Text, DateTime, DECIMAL, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import deferred

from app.models.base import Model, Base


class ServiceModel(Model, Base):
	"""
		Service Model
		ATTRIBUTES:
			id: Integer
			name: String(255)
			description: Text
			price: DECIMAL (unsigned=True)
	"""
	__tablename__ = 'services'

	id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
	name = Column(String(255), nullable=False)
	description = Column(Text, nullable=False)
	price = Column(DECIMAL(10, 2), nullable=False)
	upd_datetime = deferred(Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()))

	def __init__(self, name, description, price, upd_datetime = func.now()):
		super().__init__()
		self.name = name
		self.description = description
		self.price = price
		self.upd_datetime = upd_datetime


class RequestModel(Model, Base):
	"""
		Request Model
		ATTRIBUTES:
			id: Integer
			qta: Integer
			id_service: Integer
	"""

	__tablename__ = 'requests'

	id = Column(Integer, primary_key=True, nullable=False)
	qta = Column(Integer, nullable=False, default=1)
	id_service = Column(Integer, ForeignKey('services.id'), nullable=True)

	def __init__(self, number, id_service):
		super().__init__()
		self.number = number
		self.id_service = id_service
