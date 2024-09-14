from traceback import format_exc

from app.models.action import ActionModel
from app.models.booking import BookingModel
from app.models.confirmation import ConfirmationModel
from app.models.error import ErrorModel
from app.models.mail import MailModel
from app.models.note import BookingNoteModel, UserNoteModel
from app.models.param import ParamModel
from app.models.request import ServiceModel, RequestModel
from app.models.user import RoleModel, UserModel, SessionUserModel, TempUser, CouponModel

from utils.env import EmailEnv
from utils.tools import get_diff_dict
from utils.messages import Messages
from utils.template import Mapper


class Entity(Mapper):
	"""
		Entity class
		ATTRIBUTES:
			Booking: BookingModel

			Service: ServiceModel
			Request: RequestModel

			Role: RoleModel
			User: UserModel
			SessionUser: SessionUserModel
			TempUser: TempUser
			Coupon: CouponModel

			Param: ParamModel

			Error: ErrorModel

			Mail: MailModel

			Confirmation: ConfirmationModel

			Action: ActionModel
	"""
	Booking = BookingModel

	Service = ServiceModel
	Request = RequestModel

	Role = RoleModel
	User = UserModel
	SessionUser = SessionUserModel
	TempUser = TempUser
	Coupon = CouponModel

	Param = ParamModel

	Error = ErrorModel

	Mail = MailModel

	Confirmation = ConfirmationModel

	Action = ActionModel

	BookingNote = BookingNoteModel
	UserNote = UserNoteModel

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	@classmethod
	def generate_email(cls, booking, subject, params, _type, _receiver=None, sending_datetime=None):
		# noinspection PyBroadException
		try:
			if _receiver:
				receiver = _receiver
			elif booking.id_user == booking.upd_user:
				receiver = EmailEnv.INFO.EMAIL
			else:
				receiver = cls.User.get(cls.User.id == booking.id_user).email

			subject += Messages.MAIL_TIME.format(date=booking.date.strftime('%d-%m-%Y'), start=f'{booking.start.hour:02}:{booking.start.minute:02}')
			if isinstance(params, list):
				params = get_diff_dict(params[0], params[1])
			cls.Mail.create_mail(receiver, subject, params, _type, sending_datetime)
		except Exception:
			error = f'Prenotazione: {booking.to_dict()}\n\nSubject: {subject}\n\nParams: {params}\n\nType: {_type}\n\nReceiver: {_receiver}\n\nDatetime: {sending_datetime}\n\nError: {format_exc()}'
			cls.save_error(error)
