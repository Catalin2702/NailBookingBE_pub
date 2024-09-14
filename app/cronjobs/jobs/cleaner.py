from app.cronjobs.jobs.job import Job
from app.services.cleaner import CleanerService


class ActionCleaner(Job):
	@Job.log
	def main(self):
		CleanerService.clean_actions()


class MailCleaner(Job):
	@Job.log
	def main(self):
		CleanerService.clean_mails()


class ConfirmationCleaner(Job):
	@Job.log
	def main(self):
		CleanerService.clean_confirmations()


class ErrorCleaner(Job):
	@Job.log
	def main(self):
		CleanerService.clean_errors()


class SessionCleaner(Job):
	@Job.log
	def main(self):
		CleanerService.clean_sessions()
