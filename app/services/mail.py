from typing import Union

from app.models.mail import MailModel
from app.entities.mail import MailEntity
from app.services.service import Service


class MailService(Service):
	"""
		Mail Service
		ATTRIBUTES:
			entity: MailEntity
			actionName: str
			actionParams: dict
		METHODS:
			fulfill_request: fulfill request
			make_response: make response
	"""

	entity: MailEntity = MailEntity()

	mapped_data = {'actionName'}
	o_mapped_data = {'actionParams'}

	@classmethod
	def get_mail_entity(cls, id_mail: int) -> MailModel:
		return cls.entity.get_mail_entity(id_mail)

	@classmethod
	def get_mails_to_send(cls) -> dict[str, Union[bool, str, dict]]:
		return cls.entity.get_mails_to_send()

	@classmethod
	def generate_confirmed_mail(cls) -> dict[str, Union[bool, str, dict]]:
		return cls.entity.generate_confirmed_mail()

	@classmethod
	def generate_booked_mail(cls) -> dict[str, Union[bool, str, dict]]:
		return cls.entity.generate_booked_mail()

	@classmethod
	def generate_new_booking_mail(cls) -> dict[str, Union[bool, str, dict]]:
		return cls.entity.generate_new_booking_mail()

	@classmethod
	def generate_confirm_email_mail(cls) -> dict[str, Union[bool, str, dict]]:
		return cls.entity.generate_confirm_email_mail()

	@classmethod
	def generate_join_account_mail(cls) -> dict[str, Union[bool, str, dict]]:
		return cls.entity.generate_join_account_mail()

	@classmethod
	def generate_new_request_booking_mail(cls) -> dict[str, Union[bool, str, dict]]:
		return cls.entity.generate_new_request_booking_mail()

	@classmethod
	def generate_forgot_password_mail(cls) -> dict[str, Union[bool, str, dict]]:
		return cls.entity.generate_forgot_password_mail()