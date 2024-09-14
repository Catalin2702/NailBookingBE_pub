from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, Enum
from sqlalchemy.orm import deferred
from sqlalchemy.sql import func
from sqlalchemy.schema import CheckConstraint
from typing import Sequence

from app.models.base import Model, Base
from utils.constants import ConstViewStates, EnumDevice, EnumHomeTypes


class ViewHomeModel(Model, Base, ConstViewStates, EnumDevice):
	"""
		ViewHome Model
		ATTRIBUTES:
			type: String(20)
			device: Enum(EnumDevice)
			title: String(100)
			order: INTEGER
			description: Text
			image: String(255)
			state: BINARY
	"""

	__tablename__ = 'view_home'

	type = Column(Enum(*EnumHomeTypes.values, name=EnumHomeTypes.name), primary_key=True, nullable=False)
	device = Column(Enum(*EnumDevice.values, name=EnumDevice.name), primary_key=True, nullable=False, default=EnumDevice.GENERIC)
	title = Column(String(255), primary_key=True, nullable=False)
	order = deferred(Column(Integer, nullable=True))
	description = Column(Text, nullable=True)
	image = Column(String(255), nullable=True)
	state = deferred(Column(Boolean, nullable=False, default=True))
	upd_datetime = deferred(Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()))

	def __init__(self, _type, title, device=EnumDevice.GENERIC, order=None, description=None, image=None, upd_datetime=func.now()):
		super().__init__()
		self.type = _type
		self.device = device
		self.title = title
		self.order = order
		self.description = description
		self.image = image
		self.upd_datetime = upd_datetime

	def to_dict(self, exclude: Sequence[str] = None) -> dict:
		_excluded = exclude or ('device', 'image', 'state', 'upd_datetime')
		return {
			**super().to_dict(exclude=_excluded),
			'images': self.image.split(',') or [''],
		}


class ViewGalleryModel(Model, Base, ConstViewStates):
	"""
		ViewGallery Model
		ATTRIBUTES:
			id: INTEGER
			title: String(255)
			order: INTEGER
			description: Text
			image: String(255)
			state: BINARY
			upd_datetime: DateTime
	"""

	__tablename__ = 'view_gallery'

	id = Column(Integer, primary_key=True, autoincrement=True)
	title = deferred(Column(String(255), nullable=True))
	order = deferred(Column(Integer, nullable=True, default=0))
	description = deferred(Column(Text, nullable=True))
	image = Column(String(255), nullable=True)
	state = deferred(Column(Boolean, nullable=False, default=ConstViewStates.ACTIVE))
	upd_datetime = deferred(Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()))

	def __init__(self, title, order=None, description=None, image=None, _id=None, upd_datetime=func.now()):
		super().__init__()
		self.id = _id
		self.title = title
		self.order = order
		self.description = description
		self.image = image
		self.upd_datetime = upd_datetime


class ViewFeedbackModel(Model, Base, ConstViewStates):
	"""
		ViewFeedback Model
		ATTRIBUTES:
			id: INTEGER
			title: String(255)
			description: Text
			rating: INTEGER (1-5)
			state: BINARY
			upd_datetime: DateTime
	"""

	__tablename__ = 'view_feedback'

	id = Column(Integer, primary_key=True, autoincrement=True)
	title = Column(String(255), nullable=True)
	description = Column(Text, nullable=True)
	rating = Column(Integer, CheckConstraint('rating >= 1 AND rating <= 5'), nullable=False)
	state = deferred(Column(Boolean, nullable=False, default=ConstViewStates.ACTIVE))
	upd_datetime = deferred(Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()))

	def __init__(self, title, rating, description=None, _id=None, upd_datetime=func.now()):
		super().__init__()
		self.id = _id
		self.title = title
		self.rating = rating
		self.description = description
		self.upd_datetime = upd_datetime

	def to_dict(self, max_length=None):
		if max_length and len(self.description) > max_length:
			description = self.description[:max_length] + ' (...)'
		else:
			description = self.description
		_exclude = ('description', 'state', 'upd_datetime')
		return {
			**super().to_dict(exclude=_exclude),
			'description': description,
		}
