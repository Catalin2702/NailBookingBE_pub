from sqlalchemy import and_

from utils.constants import ConstDevice
from utils.env import SettingsEnv
from utils.exceptions import exception
from utils.tools import response, Parameter
from utils.messages import generic_error, Errors
from views.view import View


class GalleryView(View):
	"""
		View per la gestione della Gallery
	"""

	def __init__(self, **kwargs):
		kwargs['mapping'] = {
			'viewData': self.get_view_data,
			'getImageData': self.get_image_data,
			'getNextImages': self.get_next_images,
		}
		super().__init__(**kwargs)

	@classmethod
	@exception(generic_error)
	async def get_view_data(cls, **kwargs):
		try:
			_device: int = Parameter('device', kwargs, int, False, default_=ConstDevice.DESKTOP).value
		except ValueError as e:
			return response(False, str(e))
		del kwargs

		if _device <= len(SettingsEnv.MAX_GALLERY_IMAGES):
			max_images = int(SettingsEnv.MAX_GALLERY_IMAGES[_device])
		else:
			max_images = 10

		with cls.get_session() as session:
			data: list[cls.Gallery] = session.query(cls.Gallery).filter(cls.Gallery.state == True).order_by(
				cls.Gallery.order,
				cls.Gallery.upd_datetime.desc()
			).limit(max_images).all()

		return response(True, '', {'gallery':
			[
				{
					'id': item.id,
					'image': item.image,
					'loading': True
				}
				for item in data
			]
		})

	@classmethod
	@exception(generic_error)
	async def get_next_images(cls, **kwargs):
		try:
			_device: int = Parameter('device', kwargs, int, False, default_=ConstDevice.DESKTOP).value
			_len: int = Parameter('len', kwargs, int, False, default_=0).value
		except ValueError as e:
			return response(False, str(e))
		del kwargs

		if _device <= len(SettingsEnv.MAX_GALLERY_IMAGES):
			max_images = int(SettingsEnv.MAX_GALLERY_IMAGES[_device])
		else:
			max_images = 10

		with cls.get_session() as session:
			data: list[cls.Gallery] = session.query(cls.Gallery).filter(
				and_(cls.Gallery.state == cls.Gallery.ACTIVE)
			).order_by(
				cls.Gallery.order,
				cls.Gallery.upd_datetime.desc()
			).offset(_len).limit(max_images).all()

		return response(True, '', {'gallery':
			[
				{
					'id': item.id,
					'image': item.image,
				}
				for item in data
			]
		})


	@classmethod
	@exception(generic_error)
	async def get_image_data(cls, **kwargs):
		try:
			_id: int = Parameter('id', kwargs, int, True).value
		except ValueError as e:
			return response(False, str(e))
		del kwargs

		with cls.get_session(commit=False) as session:
			data: cls.Gallery = session.query(cls.Gallery).filter(
				and_(
					cls.Gallery.state == cls.Gallery.ACTIVE,
					cls.Gallery.id == _id
				)
			).first()

			if not data:
				return response(False, Errors.NO_IMAGE)

			return response(True, '', {'data': {
				'id': data.id,
				'title': data.title,
				'description': data.description,
			}})
