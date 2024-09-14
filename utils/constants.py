class Constants:
	labels = {}

	@classmethod
	def get_label(cls, key) -> str:
		return cls.labels.get(key, '')

	@classmethod
	def get(cls, key) -> str:
		return getattr(cls, key)


class Enum(Constants):
	name = ''
	values = []


class ConstDays(Constants):
	MONDAY = 0
	TUESDAY = 1
	WEDNESDAY = 2
	THURSDAY = 3
	FRIDAY = 4
	SATURDAY = 5
	SUNDAY = 6

	labels = {
		MONDAY: 'Lunedì',
		TUESDAY: 'Martedì',
		WEDNESDAY: 'Mercoledì',
		THURSDAY: 'Giovedì',
		FRIDAY: 'Venerdì',
		SATURDAY: 'Sabato',
		SUNDAY: 'Domenica',
	}


class ConstDevice(Constants):
	DESKTOP = 0
	MOBILE = 1
	GENERIC = 2

	labels = {
		DESKTOP: 'Desktop',
		MOBILE: 'Mobile',
		GENERIC: 'Generic',
	}


class ConstTheme(Constants):
	DARK = 0
	LIGHT = 1

	labels = {
		DARK: 'Dark',
		LIGHT: 'Light',
	}


class ConstViewStates(Constants):
	"""
		Status class
	"""
	INACTIVE = False
	ACTIVE = True

	labels = {
		INACTIVE: 'Inattivo',
		ACTIVE: 'Attivo',
	}


class ConstRoles(Constants):
	GUEST = 0
	ANON = 1
	USER = 2
	ADMIN = 3

	labels = {
		GUEST: 'Guest',
		ANON: 'Anon',
		USER: 'User',
		ADMIN: 'Admin',
	}


class ConstConfirmCodes(Constants):
	CONFIRM_BOOKING = '?confirm_booking={code}'
	BOOK_BOOKING = '?book_booking={code}'


class ConstActionCodes(Constants):
	NEW_BOOKING = '?new_booking={code}'
	CONFIRM_EMAIL = '?confirm_email={code}'
	JOIN_ACCOUNT = '?join_account={code}'
	REQUEST_NEW_BOOKING = '?request_new_booking={code}'
	RESTORE_PASSWORD = '/profile?restore_password={code}'


class EnumBookingStates(Enum):
	BOOKED = 'BOOKED'
	CANCELLED = 'CANCELLED'
	COMPLETED = 'COMPLETED'
	CONFIRMED = 'CONFIRMED'
	FREE = 'FREE'
	PAUSED = 'PAUSED'
	PENDING = 'PENDING'

	name = 'booking_states'
	values = [CANCELLED, BOOKED, CONFIRMED, FREE, PENDING, COMPLETED, PAUSED]
	labels = {
		CANCELLED: 'Annullato',
		BOOKED: 'Prenotato',
		CONFIRMED: 'Confermato',
		FREE: 'Libero',
		PENDING: 'In attesa',
		COMPLETED: 'Completato',
		PAUSED: 'Sospeso',
	}


class EnumMailTypes(Enum):
	REQUEST_BOOKING = 'REQUEST_BOOKING'
	BOOK_BOOKING = 'BOOK_BOOKING'
	CONFIRM_BOOKING = 'CONFIRM_BOOKING'
	UPDATE = 'UPDATE'
	CANCEL = 'CANCEL'
	RULES = 'RULES'
	GENERATE_NEW_BOOKING = 'GENERATE_NEW_BOOKING'
	CONFIRM_EMAIL = 'CONFIRM_EMAIL'
	JOIN_ACCOUNT = 'JOIN_ACCOUNT'
	REQUEST_NEW_BOOKING = 'REQUEST_NEW_BOOKING'
	FORGOT_PASSWORD = 'FORGOT_PASSWORD'

	name = 'mail_types'
	values = [BOOK_BOOKING, UPDATE, CANCEL, CONFIRM_BOOKING]
	labels = {
		BOOK_BOOKING: 'Prenotazione',
		UPDATE: 'Aggiornamento',
		CANCEL: 'Cancellazione',
		CONFIRM_BOOKING: 'Conferma',
	}

class EnumMailComponents(Enum):
	TEMPLATE = 'TEMPLATE'
	BOOKING_DETAILS = 'BOOKING_DETAILS'
	USER_DETAILS = 'USER_DETAILS'
	BUTTON = 'BUTTON'
	FOOTER = 'FOOTER'
	INFORMATION_DETAILS = 'INFORMATION_DETAILS'
	REGULATION_DETAILS = 'REGULATION_DETAILS'
	NEW_BOOKING_DETAILS = 'NEW_BOOKING_DETAILS'


class EnumMailStates(Enum):
	TO_SEND = 'TO_SEND'
	COMPLETE = 'COMPLETE'
	ERROR = 'ERROR'

	name = 'mail_states'
	values = [TO_SEND, COMPLETE, ERROR]
	labels = {
		TO_SEND: 'Da inviare',
		COMPLETE: 'Completata',
		ERROR: 'Errore',
	}


class EnumHomeTypes(Enum):
	HEADER = 'HEADER'
	SECTION = 'SECTION'
	BEFORE_AFTER = 'BEFORE_AFTER'
	CAROUSEL = 'CAROUSEL'

	name = 'home_types'
	values = [HEADER, SECTION, BEFORE_AFTER, CAROUSEL]
	labels = {
		HEADER: 'Header',
		SECTION: 'Sezione',
		BEFORE_AFTER: 'Before After',
		CAROUSEL: 'Carousel',
	}


class EnumDevice(Enum):
	DESKTOP = 'DESKTOP'
	MOBILE = 'MOBILE'
	GENERIC = 'GENERIC'

	name = 'devices'
	values = [DESKTOP, MOBILE, GENERIC]
	labels = {
		DESKTOP: 'Desktop',
		MOBILE: 'Mobile',
		GENERIC: 'Generic',
	}


class EnumConfirmationType(Enum):
	ACCEPT_BOOKING = 'ACCEPT_BOOKING'
	CONFIRM_BOOKING = 'CONFIRM_BOOKING'


class EnumActionType(Enum):
	NEW_BOOKING = 'NEW_BOOKING'
	CONFIRM_EMAIL = 'CONFIRM_EMAIL'
	JOIN_ACCOUNT = 'JOIN_ACCOUNT'
	REQUEST_NEW_BOOKING = 'REQUEST_NEW_BOOKING'
	FORGOT_PASSWORD = 'FORGOT_PASSWORD'

class SQLEvents(Enum):
	BEFORE_INSERT = 'before_insert'
	BEFORE_UPDATE = 'before_update'
	BEFORE_DELETE = 'before_delete'
	AFTER_INSERT = 'after_insert'
	AFTER_UPDATE = 'after_update'
	AFTER_DELETE = 'after_delete'


class States(Enum):
	OK = True
	KO = False

	name = 'states'
	values = [OK, KO]
	labels = {
		OK: 'Ok',
		KO: 'Ko',
	}


class Time(Enum):
	SECOND = 'SECOND'
	MINUTE = 'MINUTE'
	HOUR = 'HOUR'
	DAY = 'DAY'
	WEEK = 'WEEK'
	MONTH = 'MONTH'
	YEAR = 'YEAR'
	DAY_OF_WEEK = 'DAY_OF_WEEK'

	name = 'time'
	values = [SECOND, MINUTE, HOUR, DAY, WEEK, MONTH, YEAR, DAY_OF_WEEK]
	labels = {
		SECOND: 'second',
		MINUTE: 'minute',
		HOUR: 'hour',
		DAY: 'day',
		WEEK: 'week',
		MONTH: 'month',
		YEAR: 'year',
		DAY_OF_WEEK: 'day_of_week',
	}


class ConfigJob(Enum):
	NAME = 'NAME'
	CRON = 'CRON'
	JOB = 'JOB'

	name = 'config_job_keys'
	values = [NAME, CRON, JOB]
	labels = {
		NAME: 'name',
		CRON: 'cron',
		JOB: 'job',
	}


class ResponseReason(Enum):
	NO = 'NO'
	TYPE = 'TYPE'
