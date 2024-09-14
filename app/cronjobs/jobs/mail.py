from traceback import format_exc

from app.services.mail import MailService
from app.services.error import ErrorService
from app.cronjobs.jobs.job import Job
from app.cronjobs.utils import SendEmail
from utils.tools import print_error


class MailJob(Job):

	@Job.log
	def main(self):
		res = MailService.get_mails_to_send()
		if not res['status']:
			return
		else:
			# noinspection PyBroadException
			try:
				with SendEmail() as email_sender:
					for _mail in res['content']:
						# noinspection PyBroadException
						try:
							email_sender.send_mail(_mail)
						except:
							print_error(format_exc())
							_mail.set_error()
			except:
				print_error(format_exc())
				ErrorService.save_error()


class MailGenerateConfirmBooking(Job):

	@Job.log
	def main(self):
		MailService.generate_confirmed_mail()


class MailGenerateBookedBooking(Job):

	@Job.log
	def main(self):
		MailService.generate_booked_mail()


class MailGenerateActions(Job):

	@Job.log
	def main(self):
		MailService.generate_new_booking_mail()
		MailService.generate_confirm_email_mail()
		MailService.generate_join_account_mail()
		MailService.generate_new_request_booking_mail()


class MailGenerateForgotPassword(Job):

	@Job.log
	def main(self):
		MailService.generate_forgot_password_mail()
