from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from json import loads
from smtplib import SMTP_SSL, SMTPResponseException, SMTPRecipientsRefused, SMTPException
from string import Template
from typing import Union

from app.bucket.bucket import SupabaseBucket
from app.services.error import ErrorService
from mail.mail import mails
from utils.exceptions import exception
from utils.env import EmailEnv, SettingsEnv, InfoEnv, IconEnv
from utils.constants import Time, EnumMailTypes, EnumBookingStates, ConstConfirmCodes, EnumMailComponents, ConstActionCodes
from utils.messages import Messages


class SendEmail:
	"""
		Send Email class
	"""

	__server = None
	__host = ''
	__port = 0
	__sender = ''
	__password = ''

	def __init__(self):
		self.__port, self.__host, self.__sender, self.__password = EmailEnv.PORT, EmailEnv.HOST, EmailEnv.INFO.EMAIL, EmailEnv.INFO.TOKEN

	def __enter__(self):
		self.__server = SMTP_SSL(self.__host, self.__port)
		self.__server.login(self.__sender, self.__password)
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		if self.__server:
			try:
				self.__server.quit()
			except SMTPResponseException:
				pass

	@exception(False)
	def __send_mail(self, receiver: str, subject: str, message: str, _type: str = 'html') -> bool:
		"""
			Send an email
			:param receiver: str
			:param subject: str
			:param message: str
			:param _type: str
			:return: bool
		"""
		mail = MIMEMultipart()
		mail['From'] = self.__sender
		mail['To'] = receiver
		mail['Subject'] = subject
		mail.attach(MIMEText(message, _type))
		try:
			self.__server.sendmail(self.__sender, mail['To'], mail.as_string())
			return True
		except (SMTPResponseException, SMTPRecipientsRefused) as e:
			ErrorService.save_error(e.smtp_error)
			return False
		except SMTPException as e:
			ErrorService.save_error(e)
			return False
		except Exception as e:
			ErrorService.save_error(e)
			return False

	def send_mail(self, mail):
		"""
			Send a mail
			:param mail: Mail
		"""
		message = self.fill_template(loads(mail.params), mail.type)
		res = self.__send_mail(mail.receiver, mail.subject, message)
		if res:
			mail.set_completed(mail.id)
		else:
			mail.set_error()

	@staticmethod
	def fill_template(params: dict, _type: str) -> str:
		"""
			Fill a template with the given params
			:param params: dict
			:param _type: str
			:return: str
		"""
		template: str = mails['TEMPLATE']

		def update_html(param: Union[list, str]) -> str:
			if param:
				if isinstance(param, list):
					return f'<del>{param[0]}</del> {param[1]}' if len(param) > 1 else param[0]
				else:
					return param
			return ''

		for key, value in params.items():
			if isinstance(value, list) and any(item is None for item in value):
				params[key] = next((item for item in value if item), '')

		if 'name' not in params:
			params['name'] = ''

		if 'surname' not in params:
			params['surname'] = ''

		if 'start' in params:
			if isinstance(params['start'], list):
				params['start'] = [start[0:5] for start in params['start']]
			else:
				params['start'] = params['start'][0:5]
		if 'end' in params:
			if isinstance(params['end'], list):
				params['end'] = [end[0:5] for end in params['end']]
			else:
				params['end'] = params['end'][0:5]

		for key in params.keys():
			params[key] = params[key] or ''

		icons = {}

		for key, value in IconEnv.ICONS.items():
			icons.update({
				key + '_icon': SupabaseBucket.get_image_url('/'.join([IconEnv.SOCIAL, value['icon']])),
				key + '_link': value['url']
			})

		footer = Template(mails[EnumMailComponents.FOOTER]).safe_substitute({
			'link': SettingsEnv.URL,
			**icons
		})

		match _type:
			case EnumMailTypes.CANCEL | EnumMailTypes.UPDATE | EnumMailTypes.BOOK_BOOKING:
				status = [EnumBookingStates.get_label(state) for state in params['status']] if isinstance(params['status'], list) else EnumBookingStates.get_label(params['status'])
				params.update({
					'status': update_html(status),
					'date': update_html(params['date']),
					'start': update_html(params['start']),
					'end': update_html(params['end']),
					'note': update_html(params['note'])
				})
				booking_details = mails[EnumMailComponents.BOOKING_DETAILS]

				all_params = {
					**params,
					EnumMailComponents.BOOKING_DETAILS.lower(): Template(booking_details).safe_substitute(params)
				}
			case EnumMailTypes.CONFIRM_BOOKING:
				params.update({
					'buttonLink': SettingsEnv.URL + ConstConfirmCodes.CONFIRM_BOOKING.format(code=params['code']),
					'buttonText': Messages.CONFIRM,
					'status': EnumBookingStates.get_label(params['status']),
					'address': InfoEnv.ADDRESS,
					'phone': InfoEnv.PHONE_NUMBER,
				})
				booking_details = mails[EnumMailComponents.BOOKING_DETAILS]
				button = mails[EnumMailComponents.BUTTON]

				all_params = {
					**params,
					EnumMailComponents.BOOKING_DETAILS.lower(): Template(booking_details).safe_substitute(params),
					EnumMailComponents.BUTTON.lower(): Template(button).safe_substitute(params),
				}
			case EnumMailTypes.REQUEST_BOOKING:
				params.update({
					'buttonLink': SettingsEnv.URL + ConstConfirmCodes.BOOK_BOOKING.format(code=params['code']),
					'buttonText': Messages.ACCEPT,
					'status': EnumBookingStates.get_label(params['status']),
					'name': params['client']['name'],
					'surname': params['client']['surname'],
					'email': params['client']['email'],
					'phone': params['client']['phone'],
					'instagram': params['client']['instagram'],
					'birthday': params['client']['birthday'],
				})

				user_details = mails[EnumMailComponents.USER_DETAILS]
				booking_details = mails[EnumMailComponents.BOOKING_DETAILS]
				button = mails[EnumMailComponents.BUTTON]

				all_params = {
					**params,
					EnumMailComponents.BOOKING_DETAILS.lower(): Template(booking_details).safe_substitute(params),
					EnumMailComponents.USER_DETAILS.lower(): Template(user_details).safe_substitute(params),
					EnumMailComponents.BUTTON.lower(): Template(button).safe_substitute(params)
				}
			case EnumMailTypes.RULES:
				params.update({
					'email': InfoEnv.EMAIL,
					'phone': InfoEnv.PHONE_NUMBER,
					'address': InfoEnv.ADDRESS,
					'link_address': InfoEnv.LINK_ADDRESS,
					'bus': InfoEnv.BUS,
					'link': SettingsEnv.URL,
				})
				information_details = mails[EnumMailComponents.INFORMATION_DETAILS]
				regulation_details = mails[EnumMailComponents.REGULATION_DETAILS]
				all_params = {
					**params,
					EnumMailComponents.INFORMATION_DETAILS.lower(): Template(information_details).safe_substitute(params),
					EnumMailComponents.REGULATION_DETAILS.lower(): Template(regulation_details).safe_substitute(params),
				}
			case EnumMailTypes.GENERATE_NEW_BOOKING:
				params.update({
					'buttonLink': SettingsEnv.URL + ConstActionCodes.NEW_BOOKING.format(code=params['code']),
					'buttonText': Messages.ADD_BOOKING,
				})
				new_booking_details = mails[EnumMailComponents.NEW_BOOKING_DETAILS]
				button = mails[EnumMailComponents.BUTTON]
				all_params = {
					**params,
					EnumMailComponents.NEW_BOOKING_DETAILS.lower(): Template(new_booking_details).safe_substitute(params),
					EnumMailComponents.BUTTON.lower(): Template(button).safe_substitute(params),
				}
			case EnumMailTypes.CONFIRM_EMAIL | EnumMailTypes.JOIN_ACCOUNT:
				if _type == EnumMailTypes.CONFIRM_EMAIL:
					action = ConstActionCodes.CONFIRM_EMAIL
				else:
					action = ConstActionCodes.JOIN_ACCOUNT

				params.update({
					'buttonLink': SettingsEnv.URL + action.format(code=params['code']),
					'buttonText': Messages.CONFIRM,
				})
				user_details = mails[EnumMailComponents.USER_DETAILS]
				button = mails[EnumMailComponents.BUTTON]
				all_params = {
					**params,
					EnumMailComponents.USER_DETAILS.lower(): Template(user_details).safe_substitute(params),
					EnumMailComponents.BUTTON.lower(): Template(button).safe_substitute(params),
				}
			case EnumMailTypes.REQUEST_NEW_BOOKING:
				client = params['client']
				params.update({
					'buttonLink': SettingsEnv.URL + ConstActionCodes.REQUEST_NEW_BOOKING.format(code=params['code']),
					'buttonText': Messages.ACCEPT,
					'user_id': client.get('id_user', ''),
					'name': client.get('name', ''),
					'surname': client.get('surname', ''),
					'email': client.get('email', ''),
					'phone': client.get('phone', ''),
					'instagram': client.get('instagram', ''),
					'birthday': client.get('birthday', ''),
					'status': EnumBookingStates.get_label(params['status']),
				})
				user_details = mails[EnumMailComponents.USER_DETAILS]
				button = mails[EnumMailComponents.BUTTON]
				booking_details = mails[EnumMailComponents.BOOKING_DETAILS]
				all_params = {
					**params,
					EnumMailComponents.USER_DETAILS.lower(): Template(user_details).safe_substitute(params),
					EnumMailComponents.BUTTON.lower(): Template(button).safe_substitute(params),
					EnumMailComponents.BOOKING_DETAILS.lower(): Template(booking_details).safe_substitute(params)
				}
			case EnumMailTypes.FORGOT_PASSWORD:
				client = params['client']
				params.update({
					'buttonLink': SettingsEnv.URL + ConstActionCodes.RESTORE_PASSWORD.format(code=params['code']),
					'buttonText': Messages.RESTORE_PASSWORD_BUTTON,
					'name': client.get('name', ''),
				})
				button = mails[EnumMailComponents.BUTTON]
				all_params = {
					**params,
					EnumMailComponents.BUTTON.lower(): Template(button).safe_substitute(params),
				}
			case _:
				if 'status' in params:
					params['status'] = EnumBookingStates.get_label(params['status'])

				all_params = {
					**params,
				}

		body = Template(mails[_type]).safe_substitute(all_params)

		template_params = {
			'body': body,
			'footer': footer,
			'link': SettingsEnv.URL,
			'logo': SupabaseBucket.logo(),
		}

		return Template(template).safe_substitute(template_params)


def cron_to_dict(cron: str) -> dict[str, str]:
	cron_args = cron.split(' ')
	return {
		Time.get_label(Time.MINUTE): cron_args[0],
		Time.get_label(Time.HOUR): cron_args[1],
		Time.get_label(Time.DAY): cron_args[2],
		Time.get_label(Time.MONTH): cron_args[3],
		Time.get_label(Time.DAY_OF_WEEK): cron_args[4],
	}
