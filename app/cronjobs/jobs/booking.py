from app.cronjobs.jobs.job import Job
from app.services.booking import BookingService


class BookingCompleted(Job):
	@Job.log
	def main(self):
		BookingService.complete_bookings()
