from sqlalchemy import and_, or_

from utils.constants import EnumDevice, ConstTheme, EnumHomeTypes
from utils.tools import response, Parameter
from utils.exceptions import exception
from utils.messages import generic_error
from views.view import View


class HomeView(View):
	"""
		View per la gestione della Home
	"""

	def __init__(self, **kwargs):
		kwargs['mapping'] = {
			'viewData': self.get_view_data,
			'themeData': self.get_theme_device_data,
			'deviceData': self.get_theme_device_data,
		}
		super().__init__(**kwargs)

	@classmethod
	@exception(generic_error)
	def get_header(cls, theme: int, device: int) -> View.Home:
		with cls.get_session() as session:
			return session.query(cls.Home).filter(
				and_(
					cls.Home.type == 'HEADER',
					cls.Home.device == EnumDevice.values[device],
					cls.Home.title == ConstTheme.get_label(theme),
					cls.Home.state == cls.Home.ACTIVE,
				)
			).first()

	@classmethod
	@exception(generic_error)
	async def get_view_data(cls, **kwargs) -> dict:
		try:
			_theme: int = Parameter('theme', kwargs, int, False, default_=ConstTheme.DARK).value
			_device: int = Parameter('device', kwargs, int, False, default_=EnumDevice.DESKTOP).value
		except ValueError as e:
			return response(False, str(e))
		del kwargs

		with cls.get_session() as session:
			data: list[cls.Home] = session.query(cls.Home).filter(
				and_(
					cls.Home.state == cls.Home.ACTIVE,
					or_(
						and_(
							cls.Home.type == 'HEADER',
							cls.Home.device == EnumDevice.values[_device],
							cls.Home.title == ConstTheme.get_label(_theme),
						),
						cls.Home.type.in_([_type for _type in EnumHomeTypes.values if _type != 'HEADER'])
					)
				)
			).order_by(cls.Home.order).all()

			if not data:
				return response(True, '', {'headerImage': '', 'sections': ''})

		return response(True, '', {
			'headerImage': data[0].to_dict(),
			'sections': tuple(image.to_dict() for image in data[1:])
		})

	@classmethod
	@exception(generic_error)
	async def get_theme_device_data(cls, **kwargs) -> dict:
		try:
			_theme: int = Parameter('theme', kwargs, int, False, default_=ConstTheme.DARK).value
			_device: int = Parameter('device', kwargs, int, False, default_=EnumDevice.DESKTOP).value
		except ValueError as e:
			return response(False, str(e))
		del kwargs

		header = cls.get_header(_theme, _device)
		return response(True, '', {'headerImage': header.to_dict()})
