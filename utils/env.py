from os import environ
from json import loads


class DatabaseEnv:
	USER: str = environ.get('DB_USER', '')
	PASS: str = environ.get('DB_PASS', '')
	HOST: str = environ.get('DB_HOST', '')
	PORT: int = environ.get('DB_PORT', -1)
	NAME: str = environ.get('DB_NAME', '')
	DIALECT: str = environ.get('DB_DIALECT', '')


class RedisEnv:
	HOST: str = environ.get('REDIS_HOST', '')
	PORT: int = environ.get('REDIS_PORT', -1)


class RunningMode:

	mode: str = ''

	def __init__(self, mode='DEV'):
		self.mode = mode

	@property
	def is_dev(self) -> bool:
		return self.mode == 'DEV'

	@property
	def is_prod(self) -> bool:
		return self.mode == 'PROD'

	def __repr__(self) -> str:
		return self.mode


class SettingsEnv:
	URL: str = environ.get('URL', '')
	RUNNING_MODE = RunningMode(environ.get('RUNNING_MODE', 'DEV'))
	ALLOWED_HOSTS: list[str] = environ.get('ALLOWED_HOSTS', '').split(' ')
	MAX_GALLERY_IMAGES: list[str] = environ.get('MAX_GALLERY_IMAGES', '').split(',')
	MAX_FEEDBACK_DATA: list[str] = environ.get('MAX_FEEDBACK_DATA', '').split(',')
	TIMEZONE: str = environ.get('TIMEZONE', '')


class AdminEnv:
	EMAIL: str = environ.get('ADMIN_EMAIL', '')
	TOKEN: str = environ.get('ADMIN_TOKEN', '')


class InfoEnv:
	EMAIL: str = environ.get('INFO_EMAIL', '')
	TOKEN: str = environ.get('INFO_TOKEN', '')
	PHONE_NUMBER: str = environ.get('INFO_PHONE_NUMBER', '')
	ADDRESS: str = environ.get('INFO_ADDRESS', '')
	LINK_ADDRESS: str = environ.get('INFO_LINK_ADDRESS', '')
	BUS: str = environ.get('INFO_BUS', '')


class EmailEnv:
	PORT: int = environ.get('EMAIL_PORT', -1)
	HOST: str = environ.get('EMAIL_HOST', '')
	ATTEMPTS: int = environ.get('EMAIL_ATTEMPTS', -1)
	ADMIN = AdminEnv()
	INFO = InfoEnv()


class SupabaseEnv:
	URL: str = environ.get('SUPABASE_URL', '')
	KEY: str = environ.get('SUPABASE_KEY', '')
	MEDIA_BUCKET: str = environ.get('SUPABASE_MEDIA_BUCKET', '')

class IconEnv:
	PATH: str = environ.get('ICON_PATH', '')
	SOCIAL: str = '/'.join([PATH, environ.get('SOCIAL_PATH', '')])
	ICONS: dict = loads(open('icons.json', 'r').read())


class CatalogEnv:
	DISCOUNT: dict[str, int] = {
		'min': 25,
		'max': 50,
	}
	def __init__(self, _json: dict):
		_key = 'catalog'
		if _key in _json:
			self.DISCOUNT.update(**_json[_key])


class BookingEnv:
	MONTHS_SELECTABLE: dict[str, int] = {
		'min': -2,
		'max': 5,
	}
	def __init__(self, _json: dict):
		_key = 'booking'
		if _key in _json:
			self.MONTHS_SELECTABLE.update(**_json[_key])


class ParamsEnv:
	__file: dict = loads(open('params.json', 'r').read())
	CATALOG = CatalogEnv(__file)
	BOOKING = BookingEnv(__file)
